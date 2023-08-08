# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WebsiteMenu(models.Model):
    
    _inherit = 'website.menu'

    desplegable = fields.Boolean(string="¿Es desplegable?", default=False) 
    tipo_submenu = fields.Boolean(string="¿Mega menu extendido?", default=False)
    # tipo_submenu = fields.Selection(selection=[
    #     ('Lista','lista'),
    #     ('Cuadricula','cuadricula'),
    # ],string="Tipo de Menu")

    def write(self,vals):
        return super(WebsiteMenu, self).write(vals)

    @api.model
    def get_tree(self, website_id, menu_id=None):
        def make_tree(node):
            is_homepage = bool(node.page_id and self.env['website'].browse(website_id).homepage_id.id == node.page_id.id)
            menu_node = {
                'fields': {
                    'id': node.id,
                    'name': node.name,
                    'url': node.page_id.url if node.page_id else node.url,
                    'new_window': node.new_window,
                    'is_mega_menu': node.is_mega_menu,
                    'sequence': node.sequence,
                    'parent_id': node.parent_id.id,
                    'desplegable': node.desplegable,
                    "tipo_submenu": node.tipo_submenu,
                },
                'children': [],
                'is_homepage': is_homepage,
            }
            for child in node.child_id:
                menu_node['children'].append(make_tree(child))
            return menu_node

        menu = menu_id and self.browse(menu_id) or self.env['website'].browse(website_id).menu_id
        return make_tree(menu)