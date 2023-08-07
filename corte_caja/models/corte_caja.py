# -*- coding: utf-8 -*-
import re

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import email_split, float_is_zero
from odoo.addons import decimal_precision as dp
from odoo.http import request
import datetime


class CorteCaja(models.Model):
    _name = "corte.caja"
    _description = "Corte de Caja"
    _order = 'create_date desc'
    
    _check_company_auto = True

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirm', 'Confirmado'),
        ('cancel', 'Cancelado'),
    ], default='draft', string='Estado', copy=False, index=True, readonly=True, help="Estado de la Transferencia.")

    name = fields.Char(string='Number', required=True, copy=False,
                       readonly=True, index=True, default=lambda self: _('New'))

    partner_id = fields.Many2one('res.partner', string='Proveedor', index=True, readonly=True, states={'draft': [(
        'readonly', False)]}, domain=lambda self: [("id", "in", self.env['account.payment'].search([('state', '=', 'posted'),
                                                                                                    ('payment_type', '=', 'outbound'),
                                                                                                    ('payment_method_id.code', '=', 'manual')]).mapped("partner_id").ids)])

    user_id = fields.Many2one('res.users', string='Usuario', default=lambda self: self.env.uid, readonly=True, states={'draft': [(
        'readonly', False)]})
    fecha_inicio = fields.Date(string='Fecha inicio', index=True, readonly=True, states={
                               'draft': [('readonly', False)]}, required=True)
    fecha_fin = fields.Date(string='Fecha fin', index=True, readonly=True, states={
                            'draft': [('readonly', False)]}, required=True)
    journal_id = fields.Many2one('account.journal', string='Diario de Pago', readonly=True, states={'draft': [(
        'readonly', False)]})

    # Relaciones
    corte_caja_ids = fields.One2many('corte.caja.detalle', 'corte_caja_id', 'Detalle',
                                     copy=True, readonly=True, states={'draft': [('readonly', False)]})
    corte_caja_resumen_ids = fields.One2many('corte.caja.resumen', 'corte_caja_resumen_id',
                                             'Resumen', copy=True, readonly=True, states={'draft': [('readonly', False)]})
    corte_caja_factura_ids = fields.One2many('corte.caja.factura', 'corte_caja_factura_id',
                                             'Resumen Corte', copy=True, readonly=True, states={'draft': [('readonly', False)]})

    total_corte = fields.Float(string='Total Corte', compute="_total_corte", store=True)
    total_facturas = fields.Float(string='Total Facturas', compute="_total_facturas", store=True)
    
    company_id = fields.Many2one(comodel_name='res.company', string='Compañía',
                                 store=True, readonly=True,
                                 compute='_compute_company_id')
    
    @api.depends('journal_id')
    def _compute_company_id(self):
        for move in self:
            #move.company_id = move.journal_id.company_id or move.company_id or self.env.company
            move.company_id = self.env.company

    @api.onchange('corte_caja_ids', 'corte_caja_resumen_ids',)
    def _total_corte(self):
        suma = 0
        for linea in self.corte_caja_resumen_ids:
            suma += linea.amount
        self.total_corte = suma

    @api.onchange('corte_caja_factura_ids')
    def _total_facturas(self):
        suma = 0
        for linea in self.corte_caja_factura_ids:
            suma += linea.amount_total
        self.total_facturas = suma

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'corte.caja') or 'New'
            result = super(CorteCaja, self).create(vals)
            self.write({'state': 'confirm'})
            return result

    def _obtener_lista_diario(self):
        lista_diario = []
        for linea in self.corte_caja_ids:
            if linea.journal_id.id not in lista_diario:
                lista_diario.append(linea.journal_id.id)
        return lista_diario

    def _sumar_por_diario(self, consulta_account_payment):
        lista_diario = self._obtener_lista_diario()
        listado_sumatoria = []

        for diario in lista_diario:
            sumatoria = sum(calculo.amount for calculo in consulta_account_payment.filtered(
                lambda journal: journal.journal_id.id in (diario,)))
            dic_sumatoria = {'journal_id': diario, 'amount': sumatoria}
            listado_sumatoria.append(dic_sumatoria)
        return listado_sumatoria

    def _borrar_lineas(self):
        for rec in self:
            rec.corte_caja_ids = [(5, 0, 0)]
        for rec in self:
            rec.corte_caja_resumen_ids = [(5, 0, 0)]
        for rec in self:
            rec.corte_caja_factura_ids = [(5, 0, 0)]

    def action_procesar(self):
        self._borrar_lineas()
        self._buscar_pagos()
        self._buscar_facturas()

    def action_confirm(self):
        cont = 0
        for rec in self.corte_caja_ids:
            cont += 1
        for rec in self.corte_caja_resumen_ids:
            cont += 1
        for rec in self.corte_caja_factura_ids:
            cont += 1

        if cont == 0:
            raise Warning("Existen líneas en blanco, por favor valide.")
        else:
            self.write({'state': 'confirm'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def _buscar_facturas(self):       
        dominio = [
            ('state', '=', 'posted'),
            ('type', '=', 'out_invoice'),
            ('company_id', '=', self.env.company.id),
        ]

        if self.user_id:
            dominio += ('create_uid', '=', self.user_id.id),
        if self.fecha_inicio:
            dominio += ('invoice_date', '>=', self.fecha_inicio),
        if self.fecha_fin:
            dominio += ('invoice_date', '<=', self.fecha_fin),

        consulta_account_move = request.env['account.move'].search(dominio)

        for factura in consulta_account_move:
            self.corte_caja_factura_ids = [
                (0, 0, {'account_move_line_id': factura.id})]

        self._total_facturas()

    def _buscar_pagos(self):
        dominio = [
            ('state', '=', 'posted'),
            ('payment_type', '=', 'inbound'),
            ('company_id', '=', self.env.company.id)
        ]

        if self.user_id:
            dominio += ('create_uid', '=', self.user_id.id),
        if self.journal_id:
            dominio += ('journal_id', '=', self.journal_id.id),
        if self.fecha_inicio:
            dominio += ('payment_date', '>=', self.fecha_inicio),
        if self.fecha_fin:
            dominio += ('payment_date', '<=', self.fecha_fin),

        consulta_account_payment = request.env['account.payment'].search(
            dominio)

        for pago in consulta_account_payment:
            self.corte_caja_ids = [
                (0, 0, {'account_payment_line_id': pago.id})]

        lista_suma_diario = self._sumar_por_diario(consulta_account_payment)
        for suma_diario in lista_suma_diario:
            self.corte_caja_resumen_ids = [(0, 0, suma_diario)]

        self._total_corte()

    def _suma_diario(self, journal):
        consulta_diario = request.env['corte.caja.resumen'].search([('corte_caja_resumen_id', '=', self.id)])
        sumatoria = sum(calculo.amount for calculo in consulta_diario.filtered(lambda j: j.journal_id.id in (journal,)))
        return sumatoria

# Inicia Reporte
    def download_report(self): 
        return self.env['ir.actions.report'].search([('report_name', '=', 'corte_caja.report_corte_caja_pdf')]).report_action(self)

    def total_corte_caja(self):
        monedas=self._monedas()
        consulta_diario = self.corte_caja_ids 
     
        lista_totales=[]
        for moneda in monedas:
            total_corte = sum(calculo.amount for calculo in consulta_diario.filtered(lambda m: m.currency_id.symbol==moneda[0]))   
            d_total={
                'total': 'Total ' + str(moneda[0]) +' :'+ str(format(round(total_corte, 2), ',')),
            }
            lista_totales.append(d_total)
        return lista_totales

    def encabezado_corte_caja(self):
        lista_encabezado = []
        encabezado = {
            "origen": self.name,
            "user_id": self.user_id.name,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
        }
        lista_encabezado.append(encabezado)
        return lista_encabezado

    def _monedas(self):
        monedas_en_pagos=self.corte_caja_ids
        consulta_diario = self.corte_caja_resumen_ids 
        lista_monedas=[]
        for diario in consulta_diario:
            corte = self.corte_caja_ids.filtered(lambda d: d.journal_id.id == diario.journal_id.id)
            corte = corte.sorted(lambda pago: pago.account_payment_line_id.id)
            for diario in corte:
                moneda_simbolo = diario.currency_id.symbol
                moneda_nombre = diario.currency_id.name
                if (moneda_simbolo,moneda_nombre) not in lista_monedas:
                    lista_monedas.append((moneda_simbolo,moneda_nombre))
            for moneda in monedas_en_pagos:
                moneda_simbolo = moneda.currency_id.symbol
                moneda_nombre = moneda.currency_id.name
                if (moneda_simbolo,moneda_nombre) not in lista_monedas:
                    lista_monedas.append((moneda_simbolo,moneda_nombre))
            
        return lista_monedas

    def corte_caja_pdf(self):
        consulta_diario = self.corte_caja_resumen_ids 
        total_corte = sum(calculo.amount for calculo in consulta_diario)
        lista_monedas=self._monedas()
        
        lista_diario = []
        for diario in consulta_diario:
            lista_moneda=[]
            for moneda in lista_monedas:
                sumatoria_por_moneda=0
                lista_corte=[]
                d_moneda={
                    'moneda_id':moneda[0],
                    'moneda_name':moneda[1],
                }

                corte = self.corte_caja_ids.filtered(lambda d: d.journal_id.id == diario.journal_id.id and d.currency_id.symbol==moneda[0]  )
                corte = corte.sorted(lambda pago: pago.account_payment_line_id.id)
                for linea in corte:
                    sumatoria_por_moneda+=linea.amount
                    d_corte = {
                        "diario_id": linea.journal_id.id,
                        "account_payment_line_id": linea.account_payment_line_id.name,
                        "payment_date": linea.payment_date,
                        "circular": linea.circular,
                        "diario_name": linea.journal_id.name,
                        "partner_id": linea.partner_id.name,
                        "amount":  moneda[0] + ' ' + str(format(round(linea.amount, 2), ',')),
                        "total": moneda[0] + ' ' + str(format(round(linea.amount, 2), ','))
                    }
                    lista_corte.append(d_corte)
                if len(lista_corte)>0:
                    d_moneda['lista_corte']=lista_corte
                    d_moneda['sumatoria_por_moneda']= 'Subtotal: '+ moneda[0] + ' ' + str(format(round(sumatoria_por_moneda, 2), ','))
                    lista_moneda.append(d_moneda)
                dato_fact = {
                    "diario": diario.journal_id.name,
                    "monedas": lista_moneda,
                    "subtotal": str(moneda[0]) + ' ' + str(format(round(self._suma_diario(diario.journal_id.id), 2), ',')),
                    "total": str(moneda[0]) + ' ' + str(format(round(total_corte, 2), ',')),
                 }
            lista_diario.append(dato_fact)

        return lista_diario

    def _listado_pagos(self):
        listado_pagos=[]
        pagos=self.corte_caja_ids
        for pago in pagos:
            if pago.account_payment_line_id.id not in listado_pagos:
                listado_pagos.append(pago.account_payment_line_id.id)
        return listado_pagos

    def _listado_facturas(self):
        listado_facturas=[]
        facturas=self.corte_caja_factura_ids
        for factura in facturas:
            if factura.account_move_line_id.id not in listado_facturas and factura.invoice_payment_state != 'not_paid' :
                listado_facturas.append(factura.account_move_line_id.id)
        return listado_facturas
    
    def facturas_otros_dias(self):
        facturas=self._listado_facturas()
        pagos_aplicados=self.get_pagos_aplicados_factura(None)

        facturas_otros_dias=[]
        listado_facturas=[]
        ids_facturas=[]
        for registro in pagos_aplicados:
            if registro['move_id'] not in facturas:
                ids_facturas.append(registro['move_id'])  

        dominio=[
            ('id','in',tuple(ids_facturas)),
            ('company_id', '=', self.env.company.id)
        ] 
        sumatoria=0
        consulta_account_move = request.env['account.move'].search(dominio)
        for rec in consulta_account_move:
            # or rec.create_uid != self.user_id.id
            if self.fecha_inicio != rec.date and self.fecha_fin != rec.date:
                sumatoria+=rec.amount_total
                dic_facturas_otros_dias={
                    'id':rec.id,
                    'name':rec.name,
                    'date':rec.date,
                    'partner_id':rec.partner_id.name,
                    'amount_total':rec.amount_total,
                }
                facturas_otros_dias.append(dic_facturas_otros_dias)
        dato_fact = {
                "total": str(format(round(sumatoria, 2), ',')),
                "facturas": facturas_otros_dias,
        }
        listado_facturas.append(dato_fact)

        return listado_facturas
        
    def get_pagos_aplicados_factura(self,parametro, prefix='ml'):
        listado_ids=[]
        query = """
                SELECT ml2.id,ml2.partner_id,ml.move_name,ml2.payment_id,{}.move_id, ml2.ref, m2.date, apr.amount
                FROM account_move_line ml
                JOIN account_partial_reconcile apr on apr.debit_move_id = ml.id
                JOIN account_move_line ml2 on apr.credit_move_id = ml2.id
                JOIN account_move m2 on ml2.move_id = m2.id
                where ml.account_internal_type = 'receivable'
                and m2.date  between  %s and %s
                and m2.company_id = %s
                order by ml2.payment_id
                """.format(prefix)
        self.env.cr.execute(query, (self.fecha_inicio, self.fecha_fin,self.env.company.id,))
        query_result = self.env.cr.dictfetchall()

        for registro in query_result:
            if parametro=='pagos':
                listado_ids.append(registro['payment_id'])
            if parametro=='nota_credito':
                listado_ids.append(registro['move_id'])
            else:
                 listado_ids.append(registro)
        return listado_ids
    
    def listado_anticipos(self):
        facturas=self.get_pagos_aplicados_factura('pagos')
              
        monedas=self._monedas()
        lista_monedas=[]
        for moneda in monedas:
            lineas_anticipo=[]
            sumatoria_por_moneda=0
            d_moneda={
                'moneda_id':moneda[0],
                'moneda_name':moneda[1],
                }
            pagos = self.corte_caja_ids.filtered(lambda p: p.currency_id.symbol==moneda[0])
            for pago in pagos:
                if pago.account_payment_line_id.id not in facturas:
                    # print('PAGOS-> ',pago)
                    sumatoria_por_moneda+=pago.amount
                    moneda = pago.account_payment_line_id.currency_id.symbol
                    d_anticipo = {
                        "pago":pago.account_payment_line_id.name,
                        "partner_id":pago.partner_id.name,
                        "date":pago.payment_date,
                        "monto": moneda + str(format(round(pago.amount, 2), ',')),
                    }
                    lineas_anticipo.append(d_anticipo)
            if len(lineas_anticipo)>0:
                d_moneda['lista_anticipos']=lineas_anticipo
                d_moneda['sumatoria_por_moneda']= 'Total: '+ moneda[0] + ' ' + str(format(round(sumatoria_por_moneda, 2), ','))
                lista_monedas.append(d_moneda)

        # for moneda in lista_monedas:
        #     print('>',moneda['moneda_id'],moneda['moneda_name'], moneda['sumatoria_por_moneda'])
        #     for linea in moneda['lista_anticipos']:
        #         print('     >',linea['pago'],' ',linea['partner_id'],' ',linea['monto'])
        return lista_monedas
                
    def _invoice_payment_states(self):
        lista_estado = []
        for estado in self.corte_caja_factura_ids:
            if estado.invoice_payment_state not in lista_estado:
                lista_estado.append(estado.account_move_line_id.invoice_payment_state)
        return lista_estado

    def detalle_facturas(self):
        lista_estado=self._invoice_payment_states()

        lista_facturas = []
        listado_facturas_sin_pago=[]
        for estado in lista_estado:
            sumatoria = sum(calculo.amount_total for calculo in self.corte_caja_factura_ids.filtered(lambda f: f.invoice_payment_state in (estado,)))
            listado_facturas = []
            facturas = self.corte_caja_factura_ids.filtered(lambda d: d.invoice_payment_state in (estado,))
            facturas = facturas.sorted(lambda pago: pago.account_move_line_id.id)

            for f in facturas:
                if estado == 'not_paid':
                    estado = 'No pagadas'
                if estado == 'in_payment':
                    estado = 'En proceso de pago'
                if estado == 'paid':
                    estado = 'Pagadas'
                
                moneda = f.account_move_line_id.currency_id.symbol
                d_factura = {
                    "estado": estado,
                    "factura":f.account_move_line_id.name,
                    "partner_id":f.partner_id.name,
                    "date":f.date,
                    "monto": moneda + str(format(round(f.amount_total, 2), ',')),
                    "saldo": moneda + str(format(round(f.amount_residual, 2), ',')), 
                }
                listado_facturas.append(d_factura)
            dato_fact = {
                "estado": estado,
                "total": str(format(round(sumatoria, 2), ',')),
                "facturas": listado_facturas,
                "facturas_sin_pago": listado_facturas_sin_pago,
            }
            lista_facturas.append(dato_fact)
        return lista_facturas


    def detalle_notas_credito(self):       
        dominio = [
            ('state', '=', 'posted'),
            ('type', '=', 'out_refund'),
            ('invoice_payment_state', '=', 'paid'),
            ('company_id', '=', self.env.company.id),
        ]

        if self.user_id:
            dominio += ('create_uid', '=', self.user_id.id),
        if self.fecha_inicio:
            dominio += ('invoice_date', '>=', self.fecha_inicio),
        if self.fecha_fin:
            dominio += ('invoice_date', '<=', self.fecha_fin),

        consulta_account_move = request.env['account.move'].search(dominio)
        notas_credito=self.get_pagos_aplicados_factura('nota_credito','ml2')
        lista_nc=[]
        lista_nota_credito=[]
        sumatoria=0
        for nota_credito in consulta_account_move:
            if nota_credito.id in notas_credito:
                sumatoria+=nota_credito.amount_total
                dict_notas_credito={
                    "id":nota_credito.id,
                    "name":nota_credito.name,
                    "partner_id":nota_credito.partner_id.name,
                    "amount_total":nota_credito.amount_total,
                    "invoice_date":nota_credito.invoice_date,
                }
                lista_nc.append(dict_notas_credito)
        dato_nc = {
                "total": str(format(round(sumatoria, 2), ',')),
                "nota_credito": lista_nc,
            }
        lista_nota_credito.append(dato_nc)
        # print("dict_notas_credito->",lista_nota_credito)
        return lista_nota_credito




# Finaliza Reporte


class CorteCajaDetalle(models.Model):
    _name = "corte.caja.detalle"
    _description = "Detalle"

    # referencias a tablas
    corte_caja_id = fields.Many2one(
        'corte.caja', string='Corte de Caja', ondelete='cascade')
    account_payment_line_id = fields.Many2one(
        'account.payment', string='Pago', ondelete='cascade')

    # campos relacionados
    journal_id = fields.Many2one(
        string='Diario de Pago', related='account_payment_line_id.journal_id', store=True)
    circular = fields.Char(
        string='Circular', related='account_payment_line_id.communication', store=True)
    partner_id = fields.Many2one(
        string='Cliente', related='account_payment_line_id.partner_id', store=True)
    payment_date = fields.Date(
        string='Fecha Pago', related='account_payment_line_id.payment_date', store=True)

    amount = fields.Monetary(
        string='Monto', related='account_payment_line_id.amount', store=True)
    currency_id = fields.Many2one(
        string='Currency', related='account_payment_line_id.currency_id', store=True)


class CorteCajaResumen(models.Model):
    _name = "corte.caja.resumen"
    _description = "Resumen"

    # referencias a tablas
    corte_caja_resumen_id = fields.Many2one(
        'corte.caja', string='Corte de Caja', ondelete='cascade')
    journal_id = fields.Many2one(
        'account.journal', string='Diario', ondelete='cascade')
    amount = fields.Float(string='Monto', store=True)


class CorteCajaFactura(models.Model):
    _name = "corte.caja.factura"
    _description = "Facturas"

    # referencias a tablas
    corte_caja_factura_id = fields.Many2one(
        'corte.caja', string='Corte de Caja', ondelete='cascade')
    account_move_line_id = fields.Many2one(
        'account.move', string='Facturas', ondelete='cascade')

    # campos relacionados
    name = fields.Char(
        string='Factura', related='account_move_line_id.name', store=True)
    partner_id = fields.Many2one(
        string='Cliente', related='account_move_line_id.partner_id', store=True)
    ref = fields.Char(string='Referencia',
                      related='account_move_line_id.ref', store=True)
    date = fields.Date(string='Fecha Factura',
                       related='account_move_line_id.date', store=True)
    amount_total = fields.Monetary(string='Monto', related='account_move_line_id.amount_total', store=True)
    amount_residual = fields.Monetary(string='Saldo', related='account_move_line_id.amount_residual', store=True)
    currency_id = fields.Many2one(
        string='Currency', related='account_move_line_id.currency_id', store=True)

    invoice_payment_state = fields.Selection(
        string='Estado', related='account_move_line_id.invoice_payment_state', store=True)


class AccountMovetInherit(models.Model):
    _inherit = "account.move"

    corte_caja_id = fields.One2many('corte.caja.factura', 'account_move_line_id',
                                    'Facturas', copy=True, readonly=True, states={'draft': [('readonly', False)]})


class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    move_raw_ids = fields.One2many('corte.caja.detalle', 'account_payment_line_id',
                                   'Detalle', copy=True, readonly=True, states={'draft': [('readonly', False)]})
