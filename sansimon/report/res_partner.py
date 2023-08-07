# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date,timedelta
import logging
class AccountMove(models.Model):
    _inherit = "stock.picking"

    def get_direccion(self):
        direccion = ""
        if self.partner_id.street:
            direccion = self.partner_id.street
        if self.partner_id.street2:
            direccion = direccion + ", " + self.partner_id.street2
        if self.partner_id.city:
            direccion = direccion + ", " + self.partner_id.city
        return direccion

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    display_street = fields.Char('Direccion Completa', compute='_compute_street_name')

    def _compute_street_name(self):
        for record in self:
            direccion = ''
            if record.street:
                direccion += record.street
            if record.street2:
                direccion += " " + record.street2
            #if record.state_id:
            #    direccion += " " + record.state_id.name
            record.display_street = direccion

class ResCompany(models.Model):
    _inherit = 'res.partner'
    
    display_street = fields.Char('Direccion Completa', compute='_compute_street_name')

    def _compute_street_name(self):
        direccion = ""
        if self.partner_id.street:
            direccion = self.partner_id.street
        if self.partner_id.street2:
            direccion = direccion + " " + self.partner_id.street2
        if self.partner_id.city:
            direccion = direccion + " " + self.partner_id.city
        return direccion