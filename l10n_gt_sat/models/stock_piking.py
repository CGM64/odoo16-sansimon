from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_view_select_product_dai(self):
        lineas = self.move_line_ids_without_package
        for linea in lineas:
            if linea.product_id.product_tmpl_id.dai_id:
                if linea.qty_done == 0:
                    linea.qty_done = linea.product_uom_qty
                else:
                    linea.qty_done = 0
