# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang, format_date

from . import letras

class AccountPayment(models.Model):
    _inherit = "account.payment"

    check_no_negociable = fields.Boolean(string="No Negociable", default=False, tracking=True)
    observaciones = fields.Char(string="Observaciones",required=False)
    comentarios = fields.Char(string="Comentarios",required=False)

    partner_ref = fields.Char(string='Cod. Cliente', related='partner_id.default_code')

    def monto_letras(self):
        enletras = letras
        cantidadenletras = enletras.to_word(self.amount)
        if self.currency_id.name == 'USD':
            cantidadenletras = cantidadenletras.replace('QUETZALES','DOLARES')
        elif self.currency_id.name == 'EUR':
            cantidadenletras = cantidadenletras.resultado('QUETZALES','EUROS')
        self.check_amount_in_words = cantidadenletras
        return cantidadenletras

    def check_fill_line(self):
        amount_str = self.monto_letras()
        return amount_str and (amount_str + ' ').ljust(65, '*') or ''

    def do_print_checks(self):
        for payment in self:
            if payment.state == 'posted':
                payment.write({'state':'sent'})
        papel = self.journal_id.papel_cheque
        return self.env.ref(papel).report_action(self)
