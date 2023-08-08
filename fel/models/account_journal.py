# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = "account.journal"

    fel_setting_id = fields.Many2one('fel.setting', string="Facturacion FEL")
    fel_frases_ids = fields.One2many('account.journal.fel.frases', 'account_journal_id', string='Lineas de FEL Frases', copy=True)

class AccountJournalFelFrases(models.Model):
    _name = "account.journal.fel.frases"
    _description = "Frases FEL por diario"

    account_journal_id = fields.Many2one('account.journal', string='FEL Frases', ondelete='cascade', copy=True)
    fel_tipofrase = fields.Many2one('fel.tipofrases', string="Frases")
    fel_escenario = fields.Many2one('fel.escenario', string="Escenario")
