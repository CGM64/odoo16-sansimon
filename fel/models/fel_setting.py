# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
from lxml import etree
import logging
import base64

_logger = logging.getLogger(__name__)

class FelEscenario(models.Model):
    _name = "fel.escenario"
    _description = "Escenarios"

    name = fields.Char(string="Escenario", required=True)
    code = fields.Char(string="Codigo", required=True)
    tipofrases_id = fields.Many2one('fel.tipofrases', string = 'Tipo Frases', required=True)
    texto = fields.Char(string="Texto", help="Texto a colocar en la representacion grafica")

class FelTipoFrases(models.Model):
    _name = "fel.tipofrases"
    _description = "Tipos de Frases"

    name = fields.Char(string="Frase", required=True)
    code = fields.Char(string="Codigo", required=True)


class FelProveedor(models.Model):
    _name = "fel.proveedor"
    _description = "Proveedor de FEL"

    name = fields.Char(string="Nombre")
    code = fields.Char(string="Codigo")
    vat = fields.Char(string="Nit")

class FelSetting(models.Model):
    _name = "fel.setting"
    _description = "Configuración FEL"

    name = fields.Char(string="Descripcion")
    proveedor_id = fields.Many2one('res.partner', string='Proveedor', requiered=True, translate=True)
    usuario = fields.Char(string="Usuario")
    clave = fields.Char(string="Clave")
    token = fields.Char(string='Token')
    cod_establecimiento = fields.Char(string='Cod. Establecimiento', required=True)

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    emisor = fields.Many2one('res.partner', string='Emisor', requiered=True, translate=True)
    nombre_comercial = fields.Char(string='Nombre Comercial', requiered=True, translate=True)
    attach_xml = fields.Boolean(string='Attach XML',default=False)
    demo = fields.Boolean(string='Demo',default=True)
    #correo_emisor = fields.Char(string='Correo Emisior')
    #direccion_emisor = fields.Char(string='Correo Emisior', required=True, default='Ciudad')
    active = fields.Boolean(default=True)
