# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import fields, models


class Tag(models.Model):
    _name = "product.tag"
    _description = "Etiquetas de productos."

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Etiqueta', required=True, translate=True)
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "El nombre de esta etiqueta ya existe!"),
    ]
