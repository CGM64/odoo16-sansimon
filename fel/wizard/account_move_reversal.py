# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _


class FelAccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'

    journal_id = fields.Many2one('account.journal', string='Utilizar diario específico', domain="[('tipo_documento','in',('NCRE','NABN'))]", help='If empty, uses the journal of the journal entry to be reversed.')
    reason = fields.Char(string='Motivo', required=True)

    def reverse_moves(self):
        moves = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.move_id

        # Create default values.
        default_values_list = []
        for move in moves:
            default_values_list.append(self._prepare_default_reversal(move))

        # Handle reverse method.
        if self.refund_method == 'cancel':
            if any([vals.get('auto_post', False) for vals in default_values_list]):
                new_moves = moves._reverse_moves(default_values_list)
            else:
                new_moves = moves._reverse_moves(default_values_list, cancel=True)
                new_moves.fel_motivo = self.reason
                new_moves.invoice_payment_term_id = moves.invoice_payment_term_id
                new_moves.action_post_firmar()

        elif self.refund_method == 'modify':
            new_moves = moves._reverse_moves(default_values_list, cancel=True)
            new_moves.fel_motivo = self.reason
            new_moves.invoice_payment_term_id = moves.invoice_payment_term_id
            new_moves.action_post_firmar()
            moves_vals_list = []
            for move in moves.with_context(include_business_fields=True):
                moves_vals_list.append(move.copy_data({
                    'date': self.date or move.date,
                })[0])
            new_moves = self.env['account.move'].create(moves_vals_list)
        elif self.refund_method == 'refund':
            new_moves = moves._reverse_moves(default_values_list)
            new_moves.fel_motivo = self.reason
            new_moves.invoice_payment_term_id = moves.invoice_payment_term_id
        else:
            return

        # Create action.
        action = {
            'name': _('Reverse Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }
        if len(new_moves) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': new_moves.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', new_moves.ids)],
            })
        return action
