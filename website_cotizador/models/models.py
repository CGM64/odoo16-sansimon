# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class website_cotizador(models.Model):
#     _name = 'website_cotizador.website_cotizador'
#     _description = 'website_cotizador.website_cotizador'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
