# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class AccountAccount(models.Model):
    _inherit = "account.account"

    referencia = fields.Char(string='Referencia',
        help='Codigo de referencia de la nomenclatura anterior.')
