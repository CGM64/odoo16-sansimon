# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################

from odoo import fields, api, models, _
from odoo import tools
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_pricelists = fields.One2many('product.pricelist', compute='_get_active_pricelist',string='Sale Pricelist')

    def _get_active_pricelist(self):
        pricelist_ids = self.env['product.pricelist'].search([('display_price_on_product','=',True)])
        self.sale_pricelists = pricelist_ids


class ProductProduct(models.Model):
    _inherit = 'product.product'

    sale_pricelists = fields.One2many('product.pricelist', compute='_get_active_pricelist',string='Sale Pricelist')

    def _get_active_pricelist(self):
        pricelist_ids = self.env['product.pricelist'].search([('display_price_on_product','=',True)])
        self.sale_pricelists = pricelist_ids

class product_pricelist(models.Model):

    _inherit = "product.pricelist"

    display_price_on_product = fields.Boolean(string="Display Pricelist Price On Products", default=True)
    product_price = fields.Char(string="Price", compute="_get_product_price")

    def _get_product_price(self):
        for pricelist in self:
            if pricelist._context.get('product_temp_id',False):
                product_variant_id = self.env['product.template'].browse(pricelist._context.get('product_temp_id')).product_variant_ids[0]
                result =  pricelist.price_rule_get(product_variant_id.id, 1.0) 
                pricelist.product_price = str(pricelist.currency_id.round(result[pricelist.id][0]))
                if(pricelist.currency_id.position == 'after'):
                    pricelist.product_price = pricelist.product_price + ' ' + pricelist.currency_id.symbol
                else:
                    pricelist.product_price = pricelist.currency_id.symbol+ ' ' + pricelist.product_price  
            elif pricelist._context.get('product_id',False):
                product_id = pricelist._context.get('product_id')
                result =  pricelist.price_rule_get(product_id, 1.0)     
                pricelist.product_price = str(pricelist.currency_id.round(result[pricelist.id][0]))
                if(pricelist.currency_id.position == 'after'):
                    pricelist.product_price = pricelist.product_price + ' ' + pricelist.currency_id.symbol
                else:
                    pricelist.product_price = pricelist.currency_id.symbol+ ' ' + pricelist.product_price
            else:
                pricelist.product_price = 0