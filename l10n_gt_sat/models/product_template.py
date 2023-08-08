# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ProductDai(models.Model):
    _name = 'product.dai'
    _description = 'Arancel'

    name = fields.Char(string='Codigo', required=True)
    descripcion = fields.Char(string='Descripcion', required=True)
    porcentaje = fields.Integer(string='Porcentaje', required=True)

class ProductGrupoUtilidad(models.Model):
    _name = 'product.grupoutilidad'
    _description = 'Arancel'

    name = fields.Char(string='Descripcion', required=True)
    porcentaje = fields.Integer(string='Porcentaje', required=True)

class ProductMarca(models.Model):
    _name = 'product.marca'
    _description = 'Marca'

    name = fields.Char(string='Marca', required=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    dai_id = fields.Many2one('product.dai', string='DAI', help='Select a DAI for this product')
    grupo_utilidad_id = fields.Many2one('product.grupoutilidad', string='Grupo de Utilidad')
    marca_id = fields.Many2one('product.marca', string='Marca', help='Marca del producto.')
    sat_tipo_producto = fields.Selection([
		('bien','Bien'),
		('servicio','Servicio'),
		('exento','Excento'),
		('gas','Combustible'),
		('exp_in_ca_bien', 'Exportacion Bien in CA'),
		('imp_in_ca_bien', 'Importacion Bien in CA'),
		('imp_out_ca_bien', 'Importacion Bien out CA'),
		])

    tag_ids = fields.Many2many('product.tag', 'product_template_tags', 'tag_id', 'product_id', string='Etiquetas', help="Clasifique sus productos con etiquetas personalizadas.")

    @api.constrains('default_code')
    def _check_unique_default_code(self):
        if not self:
            return

        if not self.default_code:
            return

        if self.default_code == "":
            return

        self._cr.execute('''
            SELECT default_code
            FROM product_template
            WHERE default_code = %s AND id <> %s
        ''', (self.default_code,self.id))
        if self._cr.fetchone():
            raise ValidationError(_("El codigo de producto debe ser unico."))
