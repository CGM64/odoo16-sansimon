# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, date_utils,float_is_zero

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        rst = super(SaleAdvancePaymentInv, self).create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for sale_order in sale_orders:
            if sale_order.team_id.user_id.id == self.env.user.id:
                porcentaje_maximo=sale_order.team_id.porcentaje_maximo_lider
            else:
                porcentaje_maximo=sale_order.team_id.porcentaje_maximo
            for line in sale_order.order_line:
                if line.discount >porcentaje_maximo:
                    raise UserError(_("El porcentaje de descuento es mayor al porcentaje permitido en la linea del producto %s.") % (line.product_id.name))
        return rst