# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, date_utils,float_is_zero

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    def get_currencyUSD(self):
        tipo_cambio = 0.00
        currency = self.env['res.currency'].search([('name','=','USD')])
        tipo_cambio = currency.tipo_cambio
        return "{0:.2f}".format(tipo_cambio)