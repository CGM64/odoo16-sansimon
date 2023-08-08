# -*- coding: utf-8 -*-
import re

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import email_split, float_is_zero
from odoo.addons import decimal_precision as dp


class GsComprasGastos(models.Model):
    _inherit = 'purchase.order'

    def aplicar_pago(self):
        proveedor = self.partner_id.id
        monto = round(self.amount_total, 2)


        action = self.env.ref('l10n_gt_sat.action_account_payments_payable_sat')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_communication': self.name,
            'default_payment_type': 'outbound',
            'default_partner_type': 'supplier',
            'default_amount': self.amount_total,
            'default_partner_id': proveedor,
            #'default_payment_method_id': 4,
            #'default_journal_id': 56,
            'default_check_no_negociable': 1,
        }
        return result
