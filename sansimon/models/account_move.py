# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, date_utils,float_is_zero

import logging
import pytz

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    #Metodo heredado de la clase principal, y sobreescrito
    def action_invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        if any(not move.is_invoice(include_receipts=True) for move in self):
            raise UserError(_("Only invoices could be printed."))

        self.filtered(lambda inv: not inv.invoice_sent).write({'invoice_sent': True})
        if self.journal_id.template_print in ('template_factura'):
            return self.env.ref('sansimon.account_invoices').report_action(self)
        elif self.journal_id.template_print in ('template_ticket'):
            return self.env.ref('sansimon.account_invoices_ticket').report_action(self)

    #def action_post(self):
    #    rslt=super(AccountMove,self).action_post()
    #    if self.team_id.user_id.id == self.env.user.id:
    #        porcentaje_maximo=self.team_id.porcentaje_maximo_lider
    #    else:
    #        porcentaje_maximo=self.team_id.porcentaje_maximo
    #    for line in self.invoice_line_ids:
    #        if line.discount >porcentaje_maximo:
    #            raise UserError(_("El porcentaje de descuento es mayor al porcentaje permitido en la linea del producto %s.") % (line.product_id.name))
    #    return rslt
