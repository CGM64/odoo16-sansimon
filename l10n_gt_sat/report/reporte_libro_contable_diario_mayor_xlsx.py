# -*- coding: utf-8 -*-

from odoo import models,api


class ReporteLibroContableDiarioXlsx(models.AbstractModel):
    _name ='report.l10n_gt_sat.libro_contable_diario_xlsx'
    _description = 'reporte libro contable diario'
    _inherit = 'report.report_xlsx.abstract'

    def columns_range(self,start,end,point1,point2):
        return '{}{}:{}{}'.format(start,point1,end,point2)

    def generate_xlsx_report(self, workbook, data, data_report):

        sheet = workbook.add_worksheet('Libro Diario')
        negritaizquierda = workbook.add_format({'bold': True,'align':'left','valign':'vcenter','text_wrap':1})
        negritaderecha = workbook.add_format({'bold': True,'align':'right','valign':'vcenter','text_wrap':1})
        negritacentro = workbook.add_format({'bold': True,'align':'center','valign':'vcenter','text_wrap':1})
        celda_con_borde_alizquierda = workbook.add_format({'bold': True,'align':'left','valign':'vcenter','text_wrap':1,'border':1})
        celda_con_borde_alderecha = workbook.add_format({'bold': True,'align':'right','valign':'vcenter','text_wrap':1,'border':1})
        celda_borde_sup_inf_iz = workbook.add_format({'bold': True,'align':'left','valign':'vcenter','text_wrap':1,'top':1,'bottom':1})
        celda_borde_sup_inf_de = workbook.add_format({'num_format': '[$Q]#,##0.00','bold': True,'align':'right','valign':'vcenter','text_wrap':1,'top':1,'bottom':1})
        cantidades_sin_bordes = workbook.add_format({'num_format': '[$Q]#,##0.00','align': 'right','valign': 'vcenter','text_wrap': 1})
        totales = workbook.add_format({'bold':True,'num_format': '[$Q]#,##0.00','align':'right','valign':'vcenter','top':1,'bottom':6})
        totales_left = workbook.add_format({'bold':True,'align':'left','valign':'vcenter','top':1,'bottom':6})
        datas = self.env['libro_contable.report'].search([('id','=',data['form']['id'])],limit=1)
        jorunals=[]
        ids=list()
        if datas:
            if not datas.journal_ids:
                journals = self.env['account.journal'].search([('company_id', '=',datas.company_id.id)])
            else:
                for id in datas.journal_ids:
                    ids.append(id.id)
                journals = self.env['account.journal'].search([('id', 'in', ids)])
            contexto = {
                        'strict_range': False if not datas.date_from and not datas.date_to else True
                        ,'journal_ids': ids
                        ,'state':datas.target_move
                        ,'libro':datas.libro
                        ,'company_id':datas.company_id.id
                        ,'date_from':datas.date_from
                        ,'date_to':datas.date_to
            }
            accounts = self.env['account.account'].search([('company_id', '=', datas.company_id.id)])
            accounts_res = self.env['report.l10n_gt_sat.report_libro_contable_diario'].with_context(contexto)._get_account_move_entry(journals,accounts)
            sheet.merge_range(self.columns_range('A','L',1,1),'{} : Libro Diario'.format(datas.company_id.name),negritacentro)
            if datas.date_from:
                sheet.merge_range(self.columns_range('A','B',2,2),'Date from: {}'.format(datas.date_from))
            if datas.date_to:
                sheet.merge_range(self.columns_range('A','B',3,3),'Date to: {}'.format(datas.date_to))
            row=5
            for account in accounts_res:
                sheet.merge_range(self.columns_range('A','B',row,row),account['encabezado']['ldate'],negritaizquierda)
                sheet.merge_range(self.columns_range('C','F',row,row),account['encabezado']['journalname'],negritacentro)
                sheet.merge_range(self.columns_range('G','H',row,row),'',negritacentro)
                sheet.merge_range(self.columns_range('I','J',row,row),'',negritacentro)
                sheet.merge_range(self.columns_range('K','L',row,row),'',negritacentro)
                row+=1
                sheet.merge_range(self.columns_range('A','B',row,row),'Fecha',celda_con_borde_alizquierda)
                sheet.merge_range(self.columns_range('C','D',row,row),'Codigo',celda_con_borde_alizquierda)
                sheet.merge_range(self.columns_range('E','H',row,row),'Nombre',celda_con_borde_alizquierda)
                sheet.merge_range(self.columns_range('I','J',row,row),'Debe',celda_con_borde_alderecha)
                sheet.merge_range(self.columns_range('K','L',row,row),'Haber',celda_con_borde_alderecha)
                row+=1
                for line in account['detalle']:
                    sheet.merge_range(self.columns_range('A','B',row,row),line['ldate'],)
                    sheet.merge_range(self.columns_range('C','D',row,row),line['acode'],)
                    sheet.merge_range(self.columns_range('E','H',row,row),line['aname'],)
                    sheet.merge_range(self.columns_range('I','J',row,row),line['debit'],cantidades_sin_bordes)
                    sheet.merge_range(self.columns_range('K','L',row,row),line['credit'],cantidades_sin_bordes)
                    row+=1
                sheet.merge_range(self.columns_range('A','B',row,row),'',totales_left)
                sheet.merge_range(self.columns_range('C','H',row,row),'Total',totales_left)
                sheet.merge_range(self.columns_range('I','J',row,row),account['encabezado']['debit'],totales)
                sheet.merge_range(self.columns_range('K','L',row,row),account['encabezado']['credit'],totales)
                row+=2



class ReporteLibroContableMayorXlsx(models.AbstractModel):
    _name = 'report.l10n_gt_sat.libro_contable_mayor_xlsx'
    _description = 'reporte libro contable mayor'
    _inherit = 'report.report_xlsx.abstract'

    def columns_range(self,start,end,point1,point2):
        return '{}{}:{}{}'.format(start,point1,end,point2)


    def generate_xlsx_report(self, workbook, data, data_report):
        sheet = workbook.add_worksheet('Libro Mayor')
        negritaizquierda = workbook.add_format({'bold': True,'align':'left','valign':'vcenter','text_wrap':1})
        negritaderecha = workbook.add_format({'bold': True,'align':'right','valign':'vcenter','text_wrap':1})
        negritacentro = workbook.add_format({'bold': True,'align':'center','valign':'vcenter','text_wrap':1})
        celda_con_borde_alizquierda = workbook.add_format({'bold': True,'align':'left','valign':'vcenter','text_wrap':1,'border':1})
        celda_con_borde_alderecha = workbook.add_format({'bold': True,'align':'right','valign':'vcenter','text_wrap':1,'border':1})
        celda_borde_sup_inf_iz = workbook.add_format({'bold': True,'align':'left','valign':'vcenter','text_wrap':1,'top':1,'bottom':1})
        celda_borde_sup_inf_de = workbook.add_format({'num_format': '[$Q]#,##0.00','bold': True,'align':'right','valign':'vcenter','text_wrap':1,'top':1,'bottom':1})
        cantidades_sin_bordes = workbook.add_format({'num_format': '[$Q]#,##0.00','align': 'right','valign': 'vcenter','text_wrap': 1})
        totales = workbook.add_format({'bold':True,'num_format': '[$Q]#,##0.00','align':'right','valign':'vcenter','top':1,'bottom':6})
        totales_left = workbook.add_format({'bold':True,'align':'left','valign':'vcenter','top':1,'bottom':6})
        datas = self.env['libro_contable.report'].search([('id','=',data['form']['id'])],limit=1)
        jorunals=[]
        ids=list()
        if datas:
            if not datas.journal_ids:
                journals = self.env['account.journal'].search([('company_id', '=',datas.company_id.id)])
            else:
                for id in datas.journal_ids:
                    ids.append(id.id)
                journals = self.env['account.journal'].search([('id', 'in', ids)])
            accounts = self.env['account.account'].search([('company_id', '=', datas.company_id.id)])
            contexto = {
                        'strict_range': False if not datas.date_from and not datas.date_to else True
                        ,'journal_ids': ids
                        ,'state':datas.target_move
                        ,'libro':datas.libro
                        ,'company_id':datas.company_id.id
                        ,'date_from':datas.date_from
                        ,'date_to':datas.date_to
            }
            accounts_res, total_general = self.env['report.l10n_gt_sat.report_libro_contable_mayor'].with_context(contexto)._get_account_move_entry(journals,accounts)
            sheet.merge_range(self.columns_range('A','L',1,1),'{} : Libro Mayor'.format(datas.company_id.name),negritacentro)
            if datas.date_from:
                sheet.merge_range(self.columns_range('A','B',2,2),'Date from: {}'.format(datas.date_from))
            if datas.date_to:
                sheet.merge_range(self.columns_range('A','B',3,3),'Date to: {}'.format(datas.date_to))
            row=5
            for account in accounts_res:
                for encabezado in account['encabezado']:
                    sheet.merge_range(self.columns_range('A','B',row,row),encabezado['acode'],negritaizquierda)
                    sheet.merge_range(self.columns_range('C','F',row,row),encabezado['aname'],negritacentro)
                    credit=encabezado['credit']
                    debit=encabezado['debit']
                    balance=encabezado['balance']
                    row+=1
                    sheet.merge_range(self.columns_range('A','B',row,row),'Fecha',celda_con_borde_alizquierda)
                    sheet.merge_range(self.columns_range('C','F',row,row),'Diario',celda_con_borde_alizquierda)
                    sheet.merge_range(self.columns_range('G','H',row,row),'Debe',celda_con_borde_alderecha)
                    sheet.merge_range(self.columns_range('I','J',row,row),'Haber',celda_con_borde_alderecha)
                    sheet.merge_range(self.columns_range('K','L',row,row),'Saldo Final',celda_con_borde_alderecha)
                    row+=1
                    for line in account['detalle']:
                        sheet.merge_range(self.columns_range('A','B',row,row),line['ldate'])
                        sheet.merge_range(self.columns_range('C','F',row,row),line['jname'])
                        sheet.merge_range(self.columns_range('G','H',row,row),line['debit'],cantidades_sin_bordes)
                        sheet.merge_range(self.columns_range('I','J',row,row),line['credit'],cantidades_sin_bordes)
                        sheet.merge_range(self.columns_range('K','L',row,row),line['balance'],cantidades_sin_bordes)
                        row+=1
                    sheet.merge_range(self.columns_range('A','B',row,row),'',celda_borde_sup_inf_iz)
                    sheet.merge_range(self.columns_range('C','F',row,row),'Sub Total',celda_borde_sup_inf_iz)
                    sheet.merge_range(self.columns_range('G','H',row,row),debit,celda_borde_sup_inf_de)
                    sheet.merge_range(self.columns_range('I','J',row,row),credit,celda_borde_sup_inf_de)
                    sheet.merge_range(self.columns_range('K','L',row,row),balance,celda_borde_sup_inf_de)
                    row+=2
            for total in total_general:
                sheet.merge_range(self.columns_range('A','B',row,row),'Total',totales_left)
                sheet.merge_range(self.columns_range('C','F',row,row),'',totales_left)
                sheet.merge_range(self.columns_range('G','H',row,row),total['debit'],totales)
                sheet.merge_range(self.columns_range('I','J',row,row),total['credit'],totales)
                sheet.merge_range(self.columns_range('K','L',row,row),total['balance'],totales)
