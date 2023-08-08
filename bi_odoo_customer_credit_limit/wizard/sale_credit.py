# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class SaleCredit(models.TransientModel):
    _name = 'sale.credit.wizard'
    _description = 'Autorizacion de Credito'

    pick_ids = fields.Many2many('sale.order', 'sale_order_transfer_rel')

    def get_default(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    sale_credit_message = fields.Text(string="Message", readonly=True, default=get_default)

    def validate_credit(self):
        for picking in self.pick_ids:
            if picking:
                return picking.confirmacion_pedido()
        return False
