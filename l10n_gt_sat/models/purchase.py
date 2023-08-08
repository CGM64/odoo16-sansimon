# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang

class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"
    
    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            iva = base = isr = retencion_iva = 0
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
                        
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            aplica_calculo = False
            
            if taxes and line:
                tasa = 1
                if line.order_id.currency_id.name != 'GTQ':
                    rate = line.order_id.currency_id.with_context(date=line.order_id.date_order).rate
                    tasa = 1 / rate

                for tax in taxes.get('taxes', []):
                    impuesto = self.env['account.tax'].sudo().search([('name', '=', tax['name'])],limit=1)
                    if tax and impuesto:
                        if impuesto.impuesto_sat == 'iva':
                            iva = tax['amount']
                        if impuesto.impuesto_sat == 'isr':
                            if impuesto.amount_type == 'code':
                                aplica_calculo = True
                            isr = tax['amount']
                        if impuesto.impuesto_sat == 'retencion_iva':
                            retencion_iva = tax['amount']
                    base = tax['base']
                    if (isr != 0 or retencion_iva != 0) and aplica_calculo:
                        base = (base)*tasa
                        account_move = self.env['account.move']
                        impuesto_isr = account_move.sudo().get_amount_isr(base,'FAC')
                        line.update({
                            'price_tax': impuesto_isr/tasa,
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })
class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    def action_purchase_order_imprimir(self):
        print("Hola a todos, listo para imprimir")
        return self.env.ref('l10n_gt_sat.action_report_purchase_order').report_action(self)

    def reporte_prorrateo_compra(self):
        reporte = []
        i=1
        for line in self.order_line:
            linea = {}
            linea['item'] = i
            linea['codigo'] = line.product_id.default_code
            linea['descripcion'] = line.name
            linea['arancel'] = line.product_id.product_tmpl_id.dai_id.porcentaje if line.product_id.product_tmpl_id.dai_id else None
            linea['cantidad'] = line.product_qty
            linea['fob'] = line.price_unit
            linea['total_fob'] = line.price_total
            linea['fob_quetzales'] = i
            reporte.append(linea)
            i+=1
        return reporte

    def _create_picking(self):
        tiene_dai = False
        StockPicking = self.env['stock.picking']
        for order in self:

            for exp_dai in order.order_line.product_id:
                if exp_dai.product_tmpl_id.dai_id:
                    if exp_dai.product_tmpl_id.dai_id.porcentaje > 0:
                        tiene_dai = True

            print("----------------------Tendra dai???????????")
            print(tiene_dai)
            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                if not pickings:
                    if tiene_dai:
                        res = order._prepare_picking()
                        picking = StockPicking.create(res)

                        res_dai = order._prepare_picking()
                        picking_dai = StockPicking.create(res_dai)
                    else:
                        res = order._prepare_picking()
                        picking = StockPicking.create(res)
                else:
                    picking = pickings[0]

                if tiene_dai:
                    moves = order.order_line._create_stock_moves_sin_dai(picking)#------------------------------------------------------
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date_expected):
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()

                    moves_dai = order.order_line._create_stock_moves_con_dai(picking_dai)#------------------------------------------------------
                    moves_dai = moves_dai.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves_dai, key=lambda move: move.date_expected):
                        seq += 5
                        move.sequence = seq
                    moves_dai._action_assign()
                else:
                    moves = order.order_line._create_stock_moves(picking)#------------------------------------------------------
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date_expected):
                        seq += 5
                        move.sequence = seq
                        moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _create_stock_moves(self, picking):
        print("-------------------------------------------------------------Llego al piking")
        print(picking)
        values = []
        for line in self.filtered(lambda l: not l.display_type):
            for val in line._prepare_stock_moves(picking):
                values.append(val)
        return self.env['stock.move'].create(values)

    def _create_stock_moves_sin_dai(self, picking):
        print("-------------------------------------------------------------Llego al piking sin dai")
        print(picking)
        values = []
        for line in self.filtered(lambda l: not l.display_type and (not l.product_id.product_tmpl_id.dai_id or l.product_id.product_tmpl_id.dai_id.porcentaje == 0)):
            for val in line._prepare_stock_moves(picking):
                values.append(val)
        return self.env['stock.move'].create(values)

    def _create_stock_moves_con_dai(self, picking):
        print("-------------------------------------------------------------Llego al piking con dai")
        print(picking)
        values = []
        for line in self.filtered(lambda l: not l.display_type and l.product_id.product_tmpl_id.dai_id and l.product_id.product_tmpl_id.dai_id.porcentaje > 0):
            for val in line._prepare_stock_moves(picking):
                values.append(val)
        return self.env['stock.move'].create(values)
