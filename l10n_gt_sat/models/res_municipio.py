# -*- coding: utf-8 -*-
import re
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StateMunicipio(models.Model):
    _description = "Municipio"
    _name = 'res.state.municipio'
    _order = 'code'

    state_id = fields.Many2one('res.country.state', string='Departamento', required=True)
    name = fields.Char(string='Municipio', required=True)
    code = fields.Char(string='Codigo')

    _sql_constraints = [
        ('state_id_name_uniq', 'unique(state_id, name)', 'El nombre del municipio debe ser unico!')
    ]