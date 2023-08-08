# -*- coding: utf-8 -*-
from odoo import models ,fields , api
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('vat')
    def _check_unique_nit(self):
        if self.vat:
            valores = request.env['res.partner'].search([('vat', '=',self.vat)])
            if self.vat == "cf" or self.vat == "CF" or self.vat == "c/f" or self.vat == "C/F" or self.vat == "C/f":
                self.vat = "CF"
            else:
                if "-" in self.vat:
                    nit_ingresado = self.vat.replace('-', '')
                    if "-" in self.vat:
                        nit_bd = valores.vat.replace('-', '')
                        if nit_ingresado == nit_bd:
                            raise ValidationError(("Ya existe un contacto con este NIT"))
                else:
                    if "-" in self.vat:
                        nit_bd = valores.vat.replace('-', '')
                        if self.vat == nit_bd:
                            raise ValidationError(("Ya existe un contacto con este NIT"))
                    if self.vat == valores.vat:
                        raise ValidationError(("Ya existe un contacto con este NIT"))
                    else:
                        return
        else:
            return