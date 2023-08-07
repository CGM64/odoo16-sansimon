#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime, timedelta
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)


class credit_limit(models.Model):

    _name = 'customer.credit.limit'
    _description = 'Limite de credito del cliente'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    credit_limit_cust = fields.Float(string='Credit Limit', required=True)

    credit_limit_formula = fields.Selection([('receive_rule',
            'Receivable Amount of Customer'), ('due_date_rule',
            'Due Amount Till Days'), ('two_rule', 'Both Rules')],
            string='Credit Limit Formula')
    days = fields.Integer(string='days')

    product_category_ids = fields.Many2many('product.category',
            string='Product Category')
    product_ids = fields.One2many('customer.product',
                                  'customer_credit_pro_id',
                                  string='Product')


class product_credit(models.Model):

    _name = 'customer.product'
    _description = 'Limite de credito de los productos'

    product_id = fields.Many2one('product.product')
    customer_credit_pro_id = fields.Many2one('customer.credit.limit',
            string='Customer Credit Id')

    default_code = fields.Char('Internal Reference')
    list_price = fields.Float('Sale Price')
    standard_price = fields.Float('Cost Price')
    categ_id = fields.Many2one('product.category',
                               string='Product Category')
    type_id = fields.Selection([('consu', 'Consumable'), ('service',
                               'Service'), ('product',
                               'Storable Product')],
                               string='Credit Limit Formula')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')

    @api.onchange('product_id')
    def onchange_product(self):

        for i in self:
            i.default_code = i.product_id.default_code
            i.list_price = i.product_id.lst_price
            i.standard_price = i.product_id.standard_price
            i.categ_id = i.product_id.categ_id
            i.type_id = i.product_id.type
            i.uom_id = i.product_id.uom_id


class inherit_res_partner(models.Model):

    _inherit = 'res.partner'

    credit_limit = fields.Float(string='Credit Limit')
    credit_limit_id = fields.Many2one('customer.credit.limit',
            string='Credit Limit Rule', company_dependent=True)

    @api.onchange('credit_limit_id')
    def onchange_credit_id(self):
        if self.credit_limit_id:
            self.credit_limit = self.credit_limit_id.credit_limit_cust


class inherit_sale_order(models.Model):

    _inherit = 'sale.order'

    def confirmacion_pedido(self):
        res = self.action_confirm_combos()
        return res

    def action_confirm(self):
        check_flag = False
        message = ''
        # Devuelve true si el usuario pertenece al grupo de Administracion ventas

        user_group_manager = self.env.user.has_group('sales_team.group_sale_manager')

        total_amount = 0.0
        total = 0.0
        invoice_amout = 0.0
        pro_list = []
        if self.partner_id.credit_limit_id.product_ids:
            for products in self.partner_id.credit_limit_id.product_ids:
                pro_list.append(products.product_id.id)

        if self.partner_id.credit_limit_id.product_category_ids:
            for cate in self.partner_id.credit_limit_id.product_category_ids:
                pro_with_cate = self.env['product.product'].search([('categ_id', '=', cate.id)])
                for ids in pro_with_cate:
                    pro_list.append(ids.id)

        for order in self:
            if order.partner_id.credit_limit_id:
                if len(pro_list) >= 1:
                    for lines in order.order_line:
                        if lines.product_id.id in pro_list:
                            total_amount += lines.price_subtotal
                    total_amount = total_amount
                else:
                    total_amount = self.amount_total
                if total_amount > order.partner_id.credit_limit:
                    check_flag = True
                    message = _('1. Se alcanzó el límite de clientes, no puede confirmar la orden de venta.')

                if self.partner_id.credit_limit_id.credit_limit_formula in ('receive_rule', 'two_rule'):
                    total = self.partner_id.credit + self.amount_total
                    if self.partner_id.credit_limit < total:
                        check_flag = True
                        message = message + _('\n 2. Limite de Credito excedido. No puede confirmar la suma de los pedidos de venta con una cantidad por cobrar superior al limite de credito.')

                if self.partner_id.credit_limit_id.credit_limit_formula in ('due_date_rule', 'two_rule'):
                    account_invoice = self.env['account.move'].search([
                                ('partner_id', '=', self.partner_id.id)
                                ,('state', '=', 'posted')
                                ,('invoice_payment_state', '=', 'not_paid')
                                ,('type', 'in', ['out_invoice', 'out_refund'])
                            ])
                    days = self.partner_id.credit_limit_id.days
                    if len(self.payment_term_id.line_ids) > 0:
                        days += self.payment_term_id.line_ids[0].days
                    for invoice in account_invoice:
                        if invoice.invoice_date:
                            new_date = invoice.invoice_date + timedelta(days=days)
                            dt = str(datetime.now().date())
                            dt = datetime.strptime(dt, '%Y-%m-%d')
                            new_date = datetime.strptime(str(new_date), '%Y-%m-%d')
                            if dt >= new_date:
                                check_flag = True
                                message = message + _('\n 3. Supero la fecha del limite de credito. El cliente tiene otra factura, pendiente de liquidar. %s') % invoice.name


        if not check_flag:
            res = self.action_confirm_combos()
        else:
            if user_group_manager:
                view = self.env.ref('bi_odoo_customer_credit_limit.view_sale_credit_wizard')
                wiz = self.env['sale.credit.wizard'].create({'pick_ids': [(4, self.id)], 'sale_credit_message': message})
                context = dict(self.env.context or {})
                context['message'] = message
                return {
                    'name': _('¿Autoriza credito?'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'sale.credit.wizard',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': context,
                    }
            else:
                raise Warning(message)
