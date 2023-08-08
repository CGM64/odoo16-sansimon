# -*- coding: utf-8 -*-

import time
import datetime
from calendar import monthrange,month_name
from odoo.exceptions import UserError
from odoo import api, models, _
import sys

class ReportLibroContable(models.AbstractModel):
    _name = 'report.l10n_gt_sat.report_libro_contable_diario'
    _description = 'Reporte Libro Contable Diario'

    def _get_account_move_entry(self, journals, accounts):
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        #move_lines = {x: [] for x in journals.ids}
        #line_dias = {x: [] for x in range(1,366)}
        line_dias = {x: [] for x in range(1,368)}

        for x in range(1,368):
            move_lines = {x: [] for x in journals.ids}
            line_dias[x] = move_lines
            #line_dias.append({ x: move_lines})

        #En el siguiente paso voy a traer las variables de contexto que necesito
        init_tables, init_where_clause, init_where_params = MoveLine.with_context(company_id=self.env.context.get('company_id'), date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
        sql_sort = 'l.date, l.move_id'



        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        #Encabezando, group by dia, sum(debe), sum(haber)
        sql = ("""SELECT 0 AS lid, '' AS account_id, l.journal_id AS ljournal_id, j.name AS journalname, extract(doy from l.date) dia,  l.date AS ldate, '' AS lcode, \
            COALESCE(SUM(l.amount_currency),0.0) as amount_currency, '' AS lref, 'Initial Balance1' AS lname,\
            COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
            '' AS move_name, '' AS mmove_id, '' AS currency_code,\
            NULL AS currency_id,\
            '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
            '' AS partner_name\
            FROM account_move_line l\
            LEFT JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\

            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account a on (l.account_id = a.id)\
            WHERE l.account_id IN %s""" + filters + """ GROUP BY l.date, l.journal_id, j.name ORDER BY l.date, j.name""")
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            line_dias[row['dia']][row['ljournal_id']].append(row)

        # Get move lines base on sql query and Calculate the total balance of move lines
        #Detalle del encabezado, la suma de las cuentas por dia
        sql = ("""SELECT 0 AS lid, l.account_id AS account_id, a.code as acode, a.name as aname, l.journal_id AS ljournal_id, cast(extract(doy from l.date) as int) AS dia,  l.date AS ldate, '' AS lcode, \
            l.currency_id, sum(l.amount_currency) as amount_currency, '' AS lref, 'Initial Balance2' AS lname,\
            COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
            '' AS move_name, '' AS mmove_id, c.symbol AS currency_code,\
            NULL AS currency_id,\
            '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
            '' AS partner_name,\
            CASE WHEN COALESCE(SUM(l.debit),0.0) >0 THEN 1 ELSE 2 END AS tipo\
            FROM account_move_line l\
            LEFT JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account a on (l.account_id = a.id)\
            WHERE l.account_id IN %s""" + filters + """ GROUP BY l.date, extract(doy from l.date), l.journal_id, l.account_id, j.name, a.code, a.name, l.currency_id, c.symbol ORDER BY l.date, 25, a.code asc""")
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            line_dias[row['dia']][row['ljournal_id']].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in line_dias:
            dia = line_dias.get(account)
            for cuenta in dia:
                if dia.get(cuenta):
                    #print(dia.get(cuenta)[0])
                    res = {}
                    res['encabezado'] = dia.get(cuenta)[0]
                    detalle = []
                    for x in range(1,len(dia.get(cuenta))):
                        detalle.append(dia.get(cuenta)[x])
                    res['detalle'] = detalle
                    account_res.append(res)
        return account_res



    @api.model
    def _get_report_values(self, docids, data=None):

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]

        journals = []
        if not data['form'].get('journal_ids', []):
            journals = self.env['account.journal'].search([('company_id', '=', data['form']['company_id'][0])])
        else:
            journals = self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])

        accounts_res = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(journals,accounts)

        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': accounts_res,
            'print_journal': codes,
        }

class ReportLibroContableMayor(models.AbstractModel):
    _name = 'report.l10n_gt_sat.report_libro_contable_mayor'
    _description = 'Reporte Libro Contable Mayor'

    def _get_account_move_entry(self, journals, accounts):
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        #move_lines = {x: [] for x in journals.ids}
        #line_dias = {x: [] for x in range(1,366)}
        line_dias =  {x: [] for x in accounts.ids}


        for x in line_dias:
            line_dias[x] = {'encabezado': [], 'detalle': []}

        #En el siguiente paso voy a traer las variables de contexto que necesito
        #Comienzo a buscar los saldos iniciales de las cuentas
        init_tables, init_where_clause, init_where_params = MoveLine.with_context(company_id=self.env.context.get('company_id'), date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
        init_wheres = [""]

        if init_where_clause.strip():
            init_wheres.append(init_where_clause.strip())
        init_filters = " AND ".join(init_wheres)
        filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line','l')
        sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, NULL AS amount_currency, '' AS lref, 'Initial Balance' AS jname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
            '' AS move_name, '' AS mmove_id, '' AS currency_code,\
            NULL AS currency_id,\
            '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
            '' AS partner_name\
            FROM account_move_line l\
            LEFT JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            WHERE l.account_id IN %s""" + filters + """ GROUP BY l.account_id ORDER by l.account_id""")
        params = (tuple(accounts.ids),) + tuple(init_where_params)
        cr.execute(sql, params)
        for row in cr.dictfetchall():
            #move_lines[row.pop('account_id')].append(row)
            if row['balance'] > 0:
                row['debit'] = row['balance']
                row['credit'] = 0
            else:
                row['debit'] = 0
                row['credit'] = row['balance'] * -1

            line_dias[row['account_id']]['detalle'].append(row)
            #print(row)


        #Termino de buscar los saldos iniciales

        # Prepare sql query base on selected parameters from wizard
        sql_sort = 'l.date, l.move_id'
        tables, where_clause, where_params = MoveLine.with_context(company_id=self.env.context.get('company_id'), date_from=self.env.context.get('date_to'), date_to=False, initial_bal=True)._query_get()

        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l').replace('<', '<=')

        #Encabezando, group by dia, sum(debe), sum(haber)
        sql = ("""SELECT 0 AS lid, l.account_id AS account_id, a.name as aname, '' dia,  '' AS ldate, '' AS lcode, \
            a.code as acode, \
            COALESCE(SUM(l.amount_currency),0.0) as amount_currency, '' AS lref, 'Initial Balance1' AS lname,\
            COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
            '' AS move_name, '' AS mmove_id, '' AS currency_code,\
            NULL AS currency_id,\
            '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
            '' AS partner_name\
            FROM account_move_line l\
            LEFT JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account a on (l.account_id = a.id)\
            WHERE l.account_id IN %s""" + filters + """ GROUP BY l.account_id, a.name, a.code ORDER BY l.account_id, a.name""")
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)
        for row in cr.dictfetchall():
            line_dias[row['account_id']]['encabezado'].append(row)
            #print(row)


        sql_sort = 'l.date, l.move_id'
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        #Detalle del encabezado, la suma de las cuentas por dia
        sql = ("""SELECT 0 AS lid, l.account_id AS account_id, a.code as acode, a.name as aname, l.journal_id AS ljournal_id, j.name as jname, cast(extract(doy from l.date) as int) AS dia,  l.date AS ldate, '' AS lcode, \
            l.currency_id, sum(l.amount_currency) as amount_currency, '' AS lref, 'Initial Balance2' AS lname,\
            COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
            '' AS move_name, '' AS mmove_id, c.symbol AS currency_code,\
            NULL AS currency_id,\
            '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
            '' AS partner_name,\
            CASE WHEN COALESCE(SUM(l.debit),0.0) >0 THEN 1 ELSE 2 END AS tipo\
            FROM account_move_line l\
            LEFT JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account a on (l.account_id = a.id)\
            WHERE l.account_id IN %s""" + filters + """ GROUP BY l.account_id, a.name, l.date, extract(doy from l.date), l.journal_id, j.name, a.code, a.name, l.currency_id, c.symbol ORDER BY l.date, 25, a.code asc""")
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)
        for row in cr.dictfetchall():
            line_dias[row['account_id']]['detalle'].append(row)

        # Calculate the debit, credit and balance for Accounts


        total_general = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
        total= []
        account_res = []

        newlista = sorted(line_dias)
        for account in newlista:
            cuenta = line_dias.get(account)
            if cuenta['encabezado'] and cuenta['detalle']:
                res = {}
                detalle = []
                balance = 0
                debito = 0
                credito = 0
                res['acode'] = cuenta['encabezado'][0]['acode']

                for dia in cuenta['detalle']:
                    balance += dia['debit'] - dia['credit']
                    debito += dia['debit']
                    credito += dia['credit']
                    dia['balance'] = balance
                    detalle.append(dia)
                res['detalle'] = detalle
                encabezado = []
                for subtotal in cuenta['encabezado']:
                    subtotal['debit'] = debito
                    subtotal['credit'] = credito
                    subtotal['balance'] = balance
                    encabezado.append(subtotal)
                    total_general['debit'] += debito
                    total_general['credit'] += credito
                    total_general['balance'] += balance
                res['encabezado'] = encabezado
                account_res.append(res)
        total.append(total_general)

        account_res.sort(key=lambda x: x['acode'])

        return account_res, total



    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]

        journals = []
        if not data['form'].get('journal_ids', []):
            journals = self.env['account.journal'].search([('company_id', '=', data['form']['company_id'][0])])
        else:
            journals = self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])
        accounts = self.env['account.account'].search([('company_id', '=', data['form']['company_id'][0])],order="code")
        accounts_res, total_general = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(journals,accounts)

        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': accounts_res,
            'TotalGeneral': total_general,
            'print_journal': codes,
        }
