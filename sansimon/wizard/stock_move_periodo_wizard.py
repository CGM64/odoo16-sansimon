# -*- coding: utf-8 -*-

import calendar
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from odoo import api, fields, models, _



class StockMovePeriodoWizard(models.TransientModel):
    _name = "sansimon.stock.move.periodo"
    _description = "Informe de Inventario por Periodo"

    previous_month = datetime.today() + relativedelta(months=-1)
    days_previous_month = calendar.monthrange(previous_month.year, previous_month.month)

    fecha_inicio = fields.Date(string='Fecha Inicio', required=True, default=previous_month.strftime('%Y-%m-01'))
    fecha_fin = fields.Date(string='Fecha Fin', required=True, default=previous_month.strftime('%Y-%m-' + str(days_previous_month[1])))
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    def export_xls(self):
        self.ensure_one()
        data = {}
        data['form'] = self.read(['fecha_inicio', 'fecha_fin', 'company_id'])[0]
        return self.env['ir.actions.report'].search([('report_name', '=', 'sansimon.stock_move_periodo_report_xls'),
                ('report_type', '=', 'xlsx')], limit=1).report_action(self,data=data)
