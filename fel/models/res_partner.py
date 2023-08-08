# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
class res_partner(models.Model):
    _inherit = 'res.partner'

    cui = fields.Char(string="CUI")
    pasaporte = fields.Char(string="Pasaporte")
