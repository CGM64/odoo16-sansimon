# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = "account.journal"

    template_print = fields.Selection(selection=[
            ('template_factura', 'Plantilla Factura'),
            ('template_ticket', 'Plantilla Factura Ticket'),
        ], string='Formato de Impresion')
