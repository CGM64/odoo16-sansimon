# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date,timedelta
import logging
from odoo.http import request

class AccountMove(models.Model):
    _inherit = "stock.picking"

    def obtener_factura(self):
        account_move = request.env['account.move'].search([('invoice_origin', 'like',self.origin+'%')], limit=1)
        result = {'serie':'','no':'','blanco':''}
        result['serie'] =  account_move.fac_serie
        result['no'] = account_move.fac_numero
        result['blanco'] = " "
        return result