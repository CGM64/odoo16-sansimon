# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class Currency(models.Model):
    _inherit = 'res.currency'

    tipo_cambio = fields.Float(compute='_compute_tasa_cambio', string='Tipo de Cambio', digits=0,)

    @api.depends('rate_ids.rate')
    def _compute_tasa_cambio(self):
        for currency in self:
            currency.tipo_cambio = 1 / currency.rate
