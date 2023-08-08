# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class LibroContableReport(models.TransientModel):
    _name = "libro_contable.report"
    _description = "Reporte de Libros Contables"

    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    journal_ids = fields.Many2many('account.journal',
                                   'account_report_libro_contable_journal_rel',
                                   'account_id',
                                   'journal_id',
                                   string='Journals',
                                   domain=lambda self: [("company_id", "=", self.env.user.company_id.id)]
                                   )
    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')
    libro = fields.Selection([('diario', 'Diario'),
                            ('mayor','Mayor'),
                            ], string='Libro Contable', required=True, default='diario')

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        result['libro'] = data['form']['libro'] or False
        result['company_id'] = data['form']['company_id'][0] or False
        return result

    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['company_id','date_from', 'date_to', 'journal_ids', 'target_move','libro'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self._print_report(data)

    def _print_report(self, data):
        libro = data['form'].get('libro')
        if libro=='diario':
            return self.env.ref('l10n_gt_sat.action_report_l10n_gt_sat_diario').report_action(self, data=data, config=False)
        else:
            return self.env.ref('l10n_gt_sat.action_report_l10n_gt_sat_libro_mayor').report_action(self, data=data, config=False)

    def export_xls(self):
        self.ensure_one()
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        datas['form'] = self.read(['company_id','date_from', 'date_to', 'journal_ids', 'target_move','libro'])[0]
        used_context = self._build_contexts(datas)
        datas['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        if self.libro == 'diario':
            return self.env['ir.actions.report'].search(
                    [
                        ('report_name', '=', 'l10n_gt_sat.libro_contable_diario_xlsx'),
                        ('report_type', '=', 'xlsx')
                    ], limit=1).report_action(self,data=datas)
        else:
            return self.env['ir.actions.report'].search(
                    [
                        ('report_name', '=', 'l10n_gt_sat.libro_contable_mayor_xlsx'),
                        ('report_type', '=', 'xlsx')
                    ], limit=1).report_action(self,data=datas)
