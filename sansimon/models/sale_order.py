# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, date_utils,float_is_zero

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        rslt=super(SaleOrderInherit,self).action_confirm()
        if self.user_has_groups('sansimon.sale_group_acceso_desc'):
            porcentaje_maximo=self.team_id.porcentaje_maximo_lider
        else:
            porcentaje_maximo=self.team_id.porcentaje_maximo
        for line in self.order_line:
            if line.discount >porcentaje_maximo:
                raise UserError(_("El porcentaje de descuento es mayor al porcentaje permitido en la linea del producto %s.") % (line.product_id.name))
        return  rslt
