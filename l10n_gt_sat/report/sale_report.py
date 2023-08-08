# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

class SaleReport(models.Model):
    _inherit = 'sale.report'

    marca_id = fields.Many2one('product.marca', string='Marca', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['marca_id'] =  ", t.marca_id as marca_id"

        groupby += ', t.marca_id'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
