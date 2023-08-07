# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, date_utils,float_is_zero

class CrmTeamInherit(models.Model):
    _inherit = 'crm.team'

    porcentaje_maximo = fields.Float('Porcentaje Max', digits='Porcentaje',
    help='Este es el porcentaje máximo permitido (límite de descuento) que se puede aplicar en ordenes de compra y facturas.')
    porcentaje_maximo_lider = fields.Float('Porcentaje Max lider', digits='Porcentaje',
    help='Este es el porcentaje máximo permitido (límite de descuento) que se puede aplicar en ordenes de compra y facturas por el lider de ventas.')