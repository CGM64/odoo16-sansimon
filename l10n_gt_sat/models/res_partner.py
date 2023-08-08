# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    display_street = fields.Char('Direccion Completa', compute='_compute_street_name')
    display_website = fields.Char('Display WebSite', compute='_compute_street_name')

    default_code = fields.Char('Referencia Interna', index=True, readonly=True)

    municipio_id = fields.Many2one('res.state.municipio', string='Municipio')
    zona = fields.Char(string='Zona')

    @api.onchange('municipio_id')
    def _onchange_municipio_id(self):
        if self.municipio_id:
            self.state_id = self.municipio_id.state_id.id
            self.country_id = self.state_id.country_id.id
            
    def _compute_street_name(self):
        for record in self:
            direccion = ''
            if record.street:
                direccion += record.street
            if record.street2:
                direccion += " " + record.street2
            if record.state_id:
                direccion += ", " + record.state_id.name
            #if record.state_id:
            #    direccion += " " + record.state_id.name
            record.display_street = direccion

            if record.website:
                encontrar = record.website.rfind('/')+1
                record.display_website = record.website[encontrar:]

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)

        for partner in res:
            if not partner.default_code:
                partner.update({'default_code': self.env['ir.sequence'].next_by_code('res.partner.sequence')})
        return res

    def write(self, vals):
        res =  super(ResPartner, self).write(vals)

        for partner in self:
            if not partner.default_code:
                    partner.update({'default_code': self.env['ir.sequence'].next_by_code('res.partner.sequence')})
        return res
