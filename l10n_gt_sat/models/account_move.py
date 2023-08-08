# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"
    
    #INICIA BLOQUE DE CODIGO PARA CALCULO ISR#
    
    @api.onchange('currency_id')
    def _recalcular_isr(self):
        self._recompute_tax_lines(recompute_tax_base_amount=False)
        self._recompute_dynamic_lines(recompute_tax_base_amount=True)
        
    def get_amount_isr(self,amount_currency,tipo_dte):
        sing = -1
        
        #Obtener la base en la moneda de la compania
        amount = amount_currency
        #Si el monto es menor a Q2,500 entonces no se realiza ninguna retencion
        if amount <= 30000.0:
            return (sing * (amount * 0.05))
        elif amount > 30000.0:
            res = (amount - 30000.0) * 0.07
            return (sing * (((amount - 30000.0) * 0.07) + 1500.0))
    
    def compute_isr(self,taxes_map):
        for taxes_map_entry in taxes_map.values():
            keys = ['tax_line', 'grouping_dict','tax_base_amount','amount']
            #Validar que los keys esten en el diccionario
            for key in keys:
                    if not key in taxes_map_entry:
                        return taxes_map
            conversion_date = self.date or fields.Date.context_today(self)
            grouping_dict = taxes_map_entry['grouping_dict']
            tax_base_amount = tax_base_amount_currency = taxes_map_entry['tax_base_amount']
            amount = taxes_map_entry['amount']
            impuesto = False
            if not taxes_map_entry['tax_line']:
                account_id = self.env['account.tax.repartition.line'].search([
                    ('account_id','=',grouping_dict['account_id']),
                    ('company_id', '=', self.company_id.id),
                    ('invoice_tax_id','!=',False)
                    ])
                
                if account_id:
                    for account in account_id:
                        if account.invoice_tax_id:
                            impuesto = account.invoice_tax_id
                            break
            else:
                impuesto = taxes_map_entry['tax_line'].tax_line_id
            
            if not impuesto:
                break
            
            if impuesto.amount_type == 'code' and impuesto.impuesto_sat and impuesto.impuesto_sat == 'isr':
                tasa = 1
                if grouping_dict:
                    if 'currency_id' in grouping_dict and grouping_dict['currency_id']:
                        currency_id = taxes_map_entry['grouping_dict']['currency_id']
                        currency = self.env['res.currency'].browse(currency_id) if currency_id else False
                        
                        if grouping_dict['currency_id'] != self.company_id.currency_id.id and tax_base_amount != 0:
                            tax_base_amount_currency = currency._convert(taxes_map_entry['tax_base_amount'], self.company_currency_id, self.company_id, conversion_date)
                            tasa = tax_base_amount_currency / tax_base_amount
                    taxes_map_entry['amount'] = self.get_amount_isr(tax_base_amount_currency,self.journal_id.tipo_documento) / tasa
        return taxes_map
        
        
    
    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        """ Compute the dynamic tax lines of the journal entry.

        :param recompute_tax_base_amount: Flag forcing only the recomputation of the `tax_base_amount` field.
        """
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            ''' Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            '''
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id

            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                price_unit_wo_discount = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
                tax_type = 'sale' if move.type.startswith('out_') else 'purchase'
                is_refund = move.type in ('out_refund', 'in_refund')
            else:
                handle_price_include = False
                quantity = 1.0
                price_unit_wo_discount = base_line.amount_currency if base_line.currency_id else base_line.balance
                tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
                is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)

            balance_taxes_res = base_line.tax_ids._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
                price_unit_wo_discount,
                currency=base_line.currency_id or base_line.company_currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
            )

            if move.type == 'entry':
                repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
                repartition_tags = base_line.tax_ids.flatten_taxes_hierarchy().mapped(repartition_field).filtered(lambda x: x.repartition_type == 'base').tag_ids
                tags_need_inversion = self._tax_tags_need_inversion(move, is_refund, tax_type)
                if tags_need_inversion:
                    balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
                    for tax_res in balance_taxes_res['taxes']:
                        tax_res['tag_ids'] = base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

            return balance_taxes_res

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist, we only need one
                # to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        if not recompute_tax_base_amount:
            self.line_ids -= to_remove

        # ==== Mount base lines ====
        for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                if not recompute_tax_base_amount:
                    line.tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)

            # Assign tags on base line
            if not recompute_tax_base_amount:
                line.tag_ids = compute_all_vals['base_tags'] or [(5, 0, 0)]

            tax_exigible = True
            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

                if tax.tax_exigibility == 'on_payment':
                    tax_exigible = False

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })
                taxes_map_entry['amount'] += tax_vals['amount']
                taxes_map_entry['tax_base_amount'] += self._get_base_amount_to_display(tax_vals['base'], tax_repartition_line, tax_vals['group'])
                taxes_map_entry['grouping_dict'] = grouping_dict
            if not recompute_tax_base_amount:
                line.tax_exigible = tax_exigible

        # ==== Pre-process taxes_map ====
        taxes_map = self._preprocess_taxes_map(taxes_map)
        #Actualizar impuesto ISR
        taxes_map = self.compute_isr(taxes_map)

        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            tax_line = taxes_map_entry['tax_line']

            # The tax line is no longer used in any base lines, drop it.
            if tax_line and not taxes_map_entry['grouping_dict']:
                if not recompute_tax_base_amount:
                    self.line_ids -= tax_line
                continue

            currency_id = taxes_map_entry['grouping_dict']['currency_id']
            currency = self.env['res.currency'].browse(currency_id) if currency_id else False
            conversion_date = self.date or fields.Date.context_today(self)

            # Don't create tax lines with zero balance.
            if (currency or self.company_currency_id).is_zero(taxes_map_entry['amount']):
                if taxes_map_entry['tax_line'] and not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue

            # tax_base_amount field is expressed using the company currency.
            if currency:
                tax_base_amount = currency._convert(taxes_map_entry['tax_base_amount'], self.company_currency_id, self.company_id, conversion_date)
            else:
                tax_base_amount = taxes_map_entry['tax_base_amount']

            # Recompute only the tax_base_amount.
            if recompute_tax_base_amount:
                if taxes_map_entry['tax_line']:
                    taxes_map_entry['tax_line'].tax_base_amount = tax_base_amount
                continue

            if currency:
                amount_currency = taxes_map_entry['amount']
                balance = currency._convert(amount_currency, self.company_currency_id, self.company_id, conversion_date)
            else:
                amount_currency = 0.0
                balance = taxes_map_entry['amount']

            to_write_on_line = {
                'amount_currency': amount_currency,
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
                'tax_base_amount': tax_base_amount,
            }

            if taxes_map_entry['tax_line']:
                # Update an existing tax line.
                taxes_map_entry['tax_line'].update(to_write_on_line)
            else:
                # Create a new tax line.
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                taxes_map_entry['tax_line'] = create_method({
                    **to_write_on_line,
                    'name': tax.name,
                    'move_id': self.id,
                    'partner_id': line.partner_id.id,
                    'company_id': line.company_id.id,
                    'company_currency_id': line.company_currency_id.id,
                    'quantity': 1.0,
                    'date_maturity': False,
                    'exclude_from_invoice_tab': True,
                    'tax_exigible': tax.tax_exigibility == 'on_invoice',
                    **taxes_map_entry['grouping_dict'],
                })

            if tax_line and in_draft_mode:
                tax_line._onchange_amount_currency()
                tax_line._onchange_balance()

    no_linea = fields.Integer('Numero de Linea', compute='_compute_no_linea')

    sat_importa_in_ca = fields.Monetary(string="Importacion In CA", compute='_compute_libro_fiscal')
    sat_importa_out_ca = fields.Monetary(string="Importacion Out CA", compute='_compute_libro_fiscal')

    sat_exportacion_in_ca = fields.Monetary(string="Exportacion In CA", compute='_compute_libro_fiscal')
    sat_exportacion_out_ca = fields.Monetary(string="Exportacion Out CA", compute='_compute_libro_fiscal')

    sat_servicio = fields.Monetary(string="Servicio", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_bien = fields.Monetary(string="Bien", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_exento = fields.Monetary(string="Exento", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_peq_contri = fields.Monetary(string="Pequeño Contribuyente", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_iva = fields.Monetary(string="IVA", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_iva_porcentaje = fields.Float(string="IVA Porcentaje", compute='_compute_libro_fiscal')
    sat_subtotal = fields.Monetary(string="Subtotal", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_amount_total = fields.Monetary(string="Sat Total", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_combustible = fields.Monetary(string="Combustible", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_base = fields.Monetary(string="Base", compute='_compute_libro_fiscal', currency_field='company_currency_id')


    sat_valor_transaccion = fields.Float(string="Valor de transaccion", digits=(8, 2), readonly=True, states={'draft': [('readonly', False)]},)
    sat_gastos_transporte = fields.Float(string="Gastos de Transporte", digits=(8, 2), readonly=True, states={'draft': [('readonly', False)]},)
    sat_gastos_seguros = fields.Float(string="Gastos de Seguro", digits=(8, 2), readonly=True, states={'draft': [('readonly', False)]},)
    sat_gastos_otros = fields.Float(string="Otros Gastos", digits=(8, 2), readonly=True, states={'draft': [('readonly', False)]},)
    sat_tasa_cambio = fields.Float(string="Tasa de cambio", digits=(8, 5), readonly=True, states={'draft': [('readonly', False)]},)

    sat_invoice_id = fields.Many2one('account.move', string='Factura Relacionada')
    sat_invoice_name = fields.Char(related='sat_invoice_id.name', readonly=True, string='Invoice name')
    sat_invoice_child_ids = fields.One2many('account.move', 'sat_invoice_id', string='Invoice Links', domain=[('state', '=', 'posted')], readonly=True, states={'draft': [('readonly', False)]})

    #Estoy trabajando en solo linkiar los documentos y no utilizarlos para la carga


    fac_numero = fields.Char('Numero', copy=False, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]},)
    fac_serie = fields.Char('Serie', copy=False, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]},)

    sat_fac_numero = fields.Char(string="Numero Factura", compute='_compute_libro_fiscal')
    sat_fac_serie = fields.Char(string="Serie Factura", compute='_compute_libro_fiscal')

    journal_tipo_operacion = fields.Selection('Tipo de Operacion', related='journal_id.tipo_operacion', readonly=True)
    referencia_interna = fields.Char(string="Referencia Interna", compute='_referencia_interna')
    partner_ref = fields.Char(string='Cod. Cliente', related='partner_id.default_code')

    def _compute_no_linea(self):
        self.no_linea = 0

    #retorna toda la informacion necesaria de los calculos para la factura
    def get_detalle_factura(self):
        factura = {}
        factura_detalle = []
        factura_total = []

        total_total = total_base = total_impuestos  = total_descuento = total_sin_descuento = 0
        for detalle in self.invoice_line_ids.filtered(lambda l: l.price_total > 0):

            tasa = detalle.sat_tasa_currency_rate

            precio_sin_descuento = detalle.price_unit
            desc = round((100-detalle.discount) / 100, 10)
            precio_con_descuento = precio_sin_descuento * desc

            precio_sin_descuento = precio_sin_descuento / tasa
            precio_con_descuento = precio_con_descuento / tasa

            descuento = round((precio_sin_descuento * detalle.quantity) - (precio_con_descuento * detalle.quantity),4)

            total_descuento += descuento
            total_linea_sin_descuento = precio_sin_descuento * detalle.quantity
            total_sin_descuento += total_linea_sin_descuento

            total_con_descuento = round(precio_con_descuento * detalle.quantity,6)
            total_linea_base = round(total_con_descuento / (self.sat_iva_porcentaje/100+1),6)
            total_linea_impuestos = round(total_linea_base * (self.sat_iva_porcentaje/100),6)

            total_total += total_con_descuento
            total_base += total_linea_base
            total_impuestos += total_linea_impuestos

            linea = {
            'precio_sin_descuento': precio_sin_descuento,
            'precio_con_descuento': precio_con_descuento,
            'descuento': descuento,
            'total_con_descuento': total_con_descuento,
            'total_linea_sin_descuento': total_linea_sin_descuento,
            'total_linea_base': total_linea_base,
            'total_linea_impuestos': total_linea_impuestos,
            'dato_linea': detalle,
            }

            factura_detalle.append(linea)

        totales = {
            'total_sin_descuento': total_sin_descuento,
            'total_descuento': total_descuento,
            'total_total': total_total,
            'total_base': total_base,
            'total_impuestos': total_impuestos,
        }

        factura = {
            'detalle': factura_detalle,
            'totales': totales,
        }
        return factura

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_libro_fiscal(self):
        invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]

        for move in self:
            move.sat_iva_porcentaje = 0
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            iva_importacion = 0.0
            iva = 0.0
            currencies = set()

            total_servicio = total_servicio_iva = 0.0
            total_bien = total_bien_iva = 0.0
            sat_peq_contri = sat_exento = sat_combustible = 0.0
            sat_importa_in_ca = 0

            sat_exportacion_in_ca = sat_exportacion_out_ca = 0

            if move.fac_serie:
                move.sat_fac_serie = move.fac_serie
            else:
                if move.name:
                    move.sat_fac_serie = move.name[move.name.rfind("/")+1:move.name.find("-")]

            if move.fac_numero:
                move.sat_fac_numero = move.fac_numero
            else:
                if move.name:
                    move.sat_fac_numero = move.name[move.name.find("-")+1:len(move.name)]

            for line in move.line_ids:
                if line.product_id and line.product_id.name == 'CON Anticipo':
                    continue
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

                for impuesto in line.tax_line_id:
                    if impuesto.impuesto_sat == 'ipeq':
                        sat_peq_contri += line.balance
                    elif impuesto.impuesto_sat == 'iva':
                        move.sat_iva_porcentaje = impuesto.amount
                        iva += line.balance
                    elif impuesto.impuesto_sat in ('idp','itme'):
                        sat_exento += line.balance
                    elif impuesto.impuesto_sat == 'inguat':
                        sat_exento += line.balance
                #Cuando una factura en este caso ventas tiene iva exento, entonces no tiene tax_line_id, por esa razon se debe de ir a los tax_ids.
                es_exento = False
                if not line.tax_line_id:
                    for taxids in line.tax_ids:
                        if taxids.impuesto_sat == 'exeiva':
                            es_exento = True
                            sat_exento += line.balance

                if line.product_id and not es_exento:
                    es_peq_contribuyente = False
                    for line_imp in line.tax_ids:
                        if line_imp.impuesto_sat == 'ipeq':
                            es_peq_contribuyente = True
                    if es_peq_contribuyente:
                        sat_peq_contri += line.balance
                    elif line.product_id.sat_tipo_producto == 'gas':
                        sat_combustible += line.balance
                    elif line.product_id.sat_tipo_producto == 'exento':
                        sat_exento += line.balance
                    elif line.product_id.sat_tipo_producto == 'exp_in_ca_bien':
                        sat_exportacion_in_ca += line.balance
                    elif line.product_id.sat_tipo_producto == 'imp_out_ca_bien':
                        iva_importacion += line.balance
                    elif line.product_id.type in ('service'):
                        total_servicio += line.balance
                    else:
                        total_bien += line.balance


            if move.type == 'out_invoice':
                sign = -1
            elif move.type == 'out_refund':
                sign = -1
            else:
                sign = 1
            #move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            #move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            #move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            #move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            #move.amount_untaxed_signed = -total_untaxed
            #move.amount_tax_signed = -total_tax
            #move.amount_total_signed = abs(total) if move.type == 'entry' else -total
            #move.amount_residual_signed = total_residual
            move.sat_exento = 0
            move.sat_servicio = 0
            move.sat_bien = 0
            move.sat_iva = 0
            move.sat_subtotal = 0
            move.sat_amount_total = 0
            move.sat_peq_contri = 0
            move.sat_combustible = 0
            move.sat_base = 0
            move.sat_importa_in_ca = 0
            move.sat_importa_out_ca = 0
            move.sat_exportacion_in_ca = 0

            if move.state == 'cancel':
                move.sat_exento = 0

            elif move.journal_id.tipo_operacion == 'DUCA_IN':
                move.sat_iva = iva_importacion
                move.sat_importa_in_ca = move.sat_iva / 0.12
                move.sat_exportacion_in_ca = sign * sat_exportacion_in_ca
                move.sat_exento = 0
                move.sat_amount_total = move.sat_importa_in_ca + move.sat_iva + move.sat_exportacion_in_ca + move.sat_exento

            elif move.journal_id.tipo_operacion == 'DUCA_OUT':
                move.sat_iva = iva_importacion
                move.sat_importa_out_ca = move.sat_iva / 0.12
                move.sat_exento = 0
                move.sat_amount_total = move.sat_importa_out_ca + move.sat_iva + move.sat_exento
            else:

                move.sat_servicio = sign * total_servicio
                move.sat_bien = sign * total_bien
                move.sat_exento = sign * sat_exento
                move.sat_combustible = sign * sat_combustible
                move.sat_iva = sign * iva
                move.sat_subtotal = move.sat_servicio + move.sat_bien


                move.sat_peq_contri = sat_peq_contri
                move.sat_amount_total = move.sat_subtotal + move.sat_iva + move.sat_exento + move.sat_combustible + move.sat_peq_contri
                move.sat_base = move.sat_servicio + move.sat_bien + move.sat_combustible

            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

    class AccountMoveLine(models.Model):

        _inherit = "account.move.line"

        sat_tasa_cambio = fields.Float(string="Tasa de Cambio", compute='_compute_tasa_cambio', help="Tasa de cambio del documento")
        sat_tasa_currency_rate = fields.Float(string="Tasa Moneda", compute='_compute_tasa_moneda', store=True)

        @api.depends('currency_id')
        def _compute_tasa_moneda(self):
            for detalle in self:
                tasa = 1
                if detalle.currency_id:
                    tasa = detalle.currency_id.rate
                detalle.sat_tasa_currency_rate = tasa


        def _compute_tasa_cambio(self):
            tasa = 0.0
            for detalle in self:
                if detalle.amount_currency == 0:
                    tasa = 1
                else:
                    tasa = detalle.balance / detalle.amount_currency

                detalle.sat_tasa_cambio = tasa
