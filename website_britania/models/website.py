from _typeshed import Self
from odoo import models, fields, api


class Website(models.Model):
    inherit = 'website'

    def get_menus(self):
        return Self.env['product.public.category'].sudo().search(
            [('parent_id','=', False), ('website_id', 'in', (False, self.id))]
        )