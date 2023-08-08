# -*- coding: utf-8 -*-
from odoo import models,api
from datetime import datetime

class LibroFiscalReportXls(models.AbstractModel):
    _name = 'report.l10n_gt_sat.account_librofiscal_report_xls'
    _description = 'Reporte Fiscal XLS'
    _inherit = 'report.report_xlsx.abstract'

    workbook = None

    def _get_libro_ventas(self, libro, sheet_libro, fila, columna, format1,formato_resumen, date_format, vendedor,tipo):
        sheet_libro.set_column('A:C',10)
        sheet_libro.set_column('D:Q',15)
        if vendedor:
            sheet_libro.set_column(columna + 15,columna + 15,30)


        columnas={
        "no":['No.'], 
        "cod":['Cod.','resumido'], 
        "totdocs":['Total Docs.','resumido'], 
        "fecha":['Fecha.','resumido'], 
        "serie":['Serie.'], 
        "no_factura":['No. Factura'],
        "nit":['NIT'], 
        "nombre":['Nombre'],
        "exenta":['Exenta','resumido'], 
        "exp_out":['Exp. Fuera CA.'], 
        "exp_ca":['Exp. Centro A.','resumido'], 
        "servicios":['Servicio.','resumido'], 
        "ventas":['Ventas','resumido'], 
        "subtotal":['Subtotal'], 
        "iva":['IVA.','resumido'],
        "total":['Total.','resumido'], 
        }
        if vendedor:
            columnas['vendedor']=['Vendedor']

        columnas= dict(filter(lambda x: len(x[1]) == 2, columnas.items())) if tipo!='detallado' else columnas
        columna=0
        for col in columnas:
            sheet_libro.write(fila, columna, columnas[col][0], format1) if tipo=='detallado' else sheet_libro.write(fila, columna, columnas[col][0], format1)                   
            columna += 1
        

        fila += 1
        columna=0
        if tipo =='detallado':
            for f in libro['facturas']:
                sheet_libro.write(fila, columna, f.no_linea)
                sheet_libro.write(fila, columna + 1, f.journal_id.code)
                sheet_libro.write(fila, columna + 2, len(f))
                sheet_libro.write(fila, columna + 3, f.invoice_date, date_format)
                sheet_libro.write(fila, columna + 4, f.sat_fac_serie)
                sheet_libro.write(fila, columna + 5, f.sat_fac_numero)
                sheet_libro.write(fila, columna + 6, f.partner_id.vat if f.state not in ('cancel') else '')
                sheet_libro.write(fila, columna + 7, f.partner_id.name if f.state not in ('cancel') else 'Anulado')
                sheet_libro.write(fila, columna + 8, 0, self.fnumerico)
                sheet_libro.write(fila, columna + 9, 0, self.fnumerico)
                sheet_libro.write(fila, columna + 10, f.sat_exportacion_in_ca, self.fnumerico)
                sheet_libro.write(fila, columna + 11, f.sat_servicio, self.fnumerico)
                sheet_libro.write(fila, columna + 12, f.sat_bien, self.fnumerico)
                sheet_libro.write(fila, columna + 13, f.sat_subtotal, self.fnumerico)
                sheet_libro.write(fila, columna + 14, f.sat_iva, self.fnumerico)
                sheet_libro.write(fila, columna + 15, f.sat_amount_total, self.fnumerico)
                if vendedor:
                    sheet_libro.write(fila, columna + 16, f.invoice_user_id.name)
                fila += 1
                
            r = libro['resumen']
            sheet_libro.write(fila, columna + 10, r['sat_exportacion_in_ca'], self.money)
            sheet_libro.write(fila, columna + 11, r['servicio'], self.money)
            sheet_libro.write(fila, columna + 12, r['bien'], self.money)
            sheet_libro.write(fila, columna + 13, r['sat_subtotal_total'], self.money)
            sheet_libro.write(fila, columna + 14, r['sat_iva_total'], self.money)
            sheet_libro.write(fila, columna + 15, r['amount_total_total'], self.money)
            fila += 1
        else:
            for f in libro['resumido']:
                sheet_libro.write(fila, columna , f[1]['codigo'], date_format)
                sheet_libro.write(fila, columna + 1, f[1]['total_documentos'], self.fnumerico)
                sheet_libro.write(fila, columna + 2, f[1]['dia'], date_format)
                sheet_libro.write(fila, columna + 3, f[1]['sat_exento'], self.fnumerico)
                # sheet_libro.write(fila, columna + 4, f[1]['sat_importa_out_ca'], self.fnumerico)
                sheet_libro.write(fila, columna + 4, f[1]['sat_importa_in_ca'], self.fnumerico)
                sheet_libro.write(fila, columna + 5, f[1]['sat_servicio'], self.fnumerico)
                sheet_libro.write(fila, columna + 6, f[1]['sat_bien'], self.fnumerico)
                # sheet_libro.write(fila, columna + 8, f[1]['sat_subtotal'], self.fnumerico)
                sheet_libro.write(fila, columna + 7, f[1]['sat_iva'], self.fnumerico)
                sheet_libro.write(fila, columna + 8, f[1]['sat_amount_total'], self.fnumerico)
                fila += 1

            r = libro['resumen']
            sheet_libro.write(fila, columna + 1, r['cantidad_documentos'], self.money)
            sheet_libro.write(fila, columna + 3, r['sat_exento'], self.money)
            sheet_libro.write(fila, columna + 4, r['sat_exportacion_in_ca'], self.money)
            sheet_libro.write(fila, columna + 5, r['servicio'], self.money)
            sheet_libro.write(fila, columna + 6, r['bien'], self.money)
            # sheet_libro.write(fila, columna + 7, r['sat_subtotal_total'], self.money)
            sheet_libro.write(fila, columna + 7, r['sat_iva_total'], self.money)
            sheet_libro.write(fila, columna + 8, r['amount_total_total'], self.money)

            #RESUMEN SOLICITADO POR EVELYN
            sheet_libro.write(fila+2, 4,'Total Ventas Grabadas' , formato_resumen)
            sheet_libro.write(fila+3, 4,'Total Servicios Prestados' , formato_resumen)
            sheet_libro.write(fila+4, 4,'Total Exportaciones', formato_resumen)
            sheet_libro.write(fila+5, 4,'Total Notas de Crédito', formato_resumen)
            sheet_libro.write(fila+6, 4,'Total de Facturas Emitidas', formato_resumen)
            sheet_libro.write(fila+2, 5, r['bien'], self.money)
            sheet_libro.write(fila+3, 5, r['servicio'], self.money)
            sheet_libro.write(fila+4, 5, r['sat_exportacion_in_ca'], self.money)
            sheet_libro.write(fila+5, 5, r['cantidad_notas_credito'], self.money)
            sheet_libro.write(fila+6, 5, r['cantidad_facturas'], self.money)

            sheet_libro.write(fila+2, 7,'Venta Exenta' , formato_resumen)
            sheet_libro.write(fila+3, 7,'IVA Debito Fiscal' ,formato_resumen)
            sheet_libro.write(fila+4, 7,'Total Documentos', formato_resumen)
            sheet_libro.write(fila+5, 7,'Notas de Credito', formato_resumen)
            sheet_libro.write(fila+2, 8, r['sat_exento'], self.money)
            sheet_libro.write(fila+3, 8, r['sat_iva_total'], self.money)
            sheet_libro.write(fila+4, 8, r['cantidad_documentos'], self.money)
            sheet_libro.write(fila+5, 8, r['total_notas_credito'], self.money)

            # concepto_iva['cantidad_documentos'] =cantidad_documentos
            # concepto_iva['cantidad_facturas'] =cantidad_facturas
            # concepto_iva['cantidad_notas_credito'] =cantidad_notas_credito
            # concepto_iva['total_notas_credito'] =total_notas_credito



            fila += 1



        return sheet_libro

    def _get_libro_compras(self, libro, sheet_libro, fila, columna, format1, date_format,tipo):
        sheet_libro.set_column('A:C',10)
        sheet_libro.set_column('D:S',15)

        columnas={
            "no":['No.'], 
            "cod":['Cod.','resumido'], 
            "totdocs":['Total Docs.','resumido'], 
            "fecha":['Fecha.','resumido'], 
            "serie":['Serie.'], 
            "no_factura":['No. Factura'],
            "nit":['NIT'], 
            "nombre":['Nombre'],
            "exenta":['Exenta','resumido'], 
            "imp_out":['Importacion fuera CA','resumido'],
            "imp_ca":['Importacion CA','resumido'],
            "servicios":['Servicios','resumido'],
            "compra_activos":['Compra de activos fijos','resumido'],
            "pequenio_cont":['Pequeño Contrib.','resumido'],
            "bienes":['Bienes.','resumido'],
            "combustible":['Combust.','resumido'],
            "base_compras":['Base para Compras'],
            "iva":['IVA.','resumido'],
            "total":['Total','resumido'],  
        }

        columnas= dict(filter(lambda x: len(x[1]) == 2, columnas.items())) if tipo!='detallado' else columnas 
        c=0
        for col in columnas:
            sheet_libro.write(fila, c, columnas[col][0], format1) if tipo=='detallado' else sheet_libro.write(fila, c, columnas[col][0], format1)                   
            c += 1

        fila += 1
        if tipo=='detallado':
            for f in libro['facturas']:
                sheet_libro.write(fila, columna, f.no_linea)
                sheet_libro.write(fila, columna + 1, f.journal_id.code)
                sheet_libro.write(fila, columna + 2, len(f))
                sheet_libro.write(fila, columna + 3, f.invoice_date, date_format)
                sheet_libro.write(fila, columna + 4, f.sat_fac_serie)
                sheet_libro.write(fila, columna + 5, f.sat_fac_numero)
                sheet_libro.write(fila, columna + 6, f.partner_id.vat)
                sheet_libro.write(fila, columna + 7, f.partner_id.name)
                sheet_libro.write(fila, columna + 8, f.sat_exento, self.fnumerico)
                sheet_libro.write(fila, columna + 9, f.sat_importa_out_ca, self.fnumerico)
                sheet_libro.write(fila, columna + 10, f.sat_importa_in_ca, self.fnumerico)
                sheet_libro.write(fila, columna + 11, f.sat_servicio, self.fnumerico)
                sheet_libro.write(fila, columna + 12, 0, self.fnumerico)
                sheet_libro.write(fila, columna + 13, f.sat_peq_contri, self.fnumerico)
                sheet_libro.write(fila, columna + 14, f.sat_bien, self.fnumerico)
                sheet_libro.write(fila, columna + 15, f.sat_combustible, self.fnumerico)
                sheet_libro.write(fila, columna + 16, f.sat_base, self.fnumerico)
                sheet_libro.write(fila, columna + 17, f.sat_iva, self.fnumerico)
                sheet_libro.write(fila, columna + 18, f.sat_amount_total, self.fnumerico)
                fila += 1
            r = libro['resumen']
            sheet_libro.write(fila, columna + 9, r['sat_exento'], self.money)
            sheet_libro.write(fila, columna + 10, r['sat_importa_out_ca'], self.money)
            sheet_libro.write(fila, columna + 11, r['sat_importa_in_ca'], self.money)
            sheet_libro.write(fila, columna + 12, r['servicio'], self.money)
            sheet_libro.write(fila, columna + 13, r['sat_peq_contri'], self.money)
            sheet_libro.write(fila, columna + 14, r['bien'], self.money)
            sheet_libro.write(fila, columna + 15, r['sat_combustible'], self.money)
            sheet_libro.write(fila, columna + 16, r['sat_base'], self.money)
            sheet_libro.write(fila, columna + 17, r['sat_iva_total'], self.money)
            sheet_libro.write(fila, columna + 18, r['amount_total_total'], self.money)
            fila += 1
        else:
            for f in libro['resumido']:
                sheet_libro.write(fila, columna ,    f[1]['codigo'], date_format)
                sheet_libro.write(fila, columna + 1, f[1]['total_documentos'], self.fnumerico)
                sheet_libro.write(fila, columna + 2, f[1]['dia'], date_format)
                sheet_libro.write(fila, columna + 3, f[1]['sat_exento'], self.fnumerico)
                sheet_libro.write(fila, columna + 4, f[1]['sat_importa_out_ca'], self.fnumerico)
                sheet_libro.write(fila, columna + 5, f[1]['sat_importa_in_ca'], self.fnumerico)
                sheet_libro.write(fila, columna + 6, f[1]['sat_servicio'], self.fnumerico)
                sheet_libro.write(fila, columna + 7, f[1]['sat_peq_contri'], self.fnumerico)
                sheet_libro.write(fila, columna + 8, f[1]['sat_bien'], self.fnumerico)
                sheet_libro.write(fila, columna + 9, f[1]['sat_combustible'], self.fnumerico)
                sheet_libro.write(fila, columna + 10, f[1]['sat_base'], self.fnumerico)
                sheet_libro.write(fila, columna + 11, f[1]['sat_iva'], self.fnumerico)
                sheet_libro.write(fila, columna + 12, f[1]['sat_amount_total'], self.fnumerico)
                fila += 1
            r = libro['resumen']
            sheet_libro.write(fila, columna + 3, r['sat_exento'], self.money)
            sheet_libro.write(fila, columna + 4, r['sat_importa_out_ca'], self.money)
            sheet_libro.write(fila, columna + 5, r['sat_importa_in_ca'], self.money)
            sheet_libro.write(fila, columna + 6, r['servicio'], self.money)
            sheet_libro.write(fila, columna + 7, r['sat_peq_contri'], self.money)
            sheet_libro.write(fila, columna + 8, r['bien'], self.money)
            sheet_libro.write(fila, columna + 9, r['sat_combustible'], self.money)
            sheet_libro.write(fila, columna + 10, r['sat_base'], self.money)
            sheet_libro.write(fila, columna + 11, r['sat_iva_total'], self.money)
            sheet_libro.write(fila, columna + 12, r['amount_total_total'], self.money)
            fila += 1

        sheet_libro = self.workbook.add_worksheet("Resumen " + libro['descripcion'])

        fila = 0
        sheet_libro.set_column(columna,columna,15)
        sheet_libro.set_column(columna + 1,columna + 1,12)
        sheet_libro.set_column(columna + 2,columna + 2,12)
        sheet_libro.set_column(columna + 3,columna + 3,12)

        sheet_libro.write(fila, columna, "Concepto", self.bold)
        sheet_libro.write(fila, columna + 1, "Base Imponible", self.bold)
        sheet_libro.write(fila, columna + 2, "IVA", self.bold)
        sheet_libro.write(fila, columna + 3, "Total", self.bold)

        fila += 1
        sheet_libro.write(fila, columna, "Servicio")
        sheet_libro.write(fila, columna + 1, r['servicio'], self.fnumerico)
        sheet_libro.write(fila, columna + 2, r['servicio_iva'], self.fnumerico)
        sheet_libro.write(fila, columna + 3, r['servicio_total'], self.fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "Bienes")
        sheet_libro.write(fila, columna + 1, r['bien'], self.fnumerico)
        sheet_libro.write(fila, columna + 2, r['bien_iva'], self.fnumerico)
        sheet_libro.write(fila, columna + 3, r['bien_total'], self.fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "Pequeño Contribuyente")
        sheet_libro.write(fila, columna + 1, r['sat_peq_contri'], self.fnumerico)
        sheet_libro.write(fila, columna + 2, 0, self.fnumerico)
        sheet_libro.write(fila, columna + 3, r['sat_peq_contri'], self.fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "Combustible")
        sheet_libro.write(fila, columna + 1, r['sat_combustible'], self.fnumerico)
        sheet_libro.write(fila, columna + 2, r['sat_combustible_iva'], self.fnumerico)
        sheet_libro.write(fila, columna + 3, r['sat_combustible_total'], self.fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "Importacion CA")
        sheet_libro.write(fila, columna + 1, r['sat_importa_in_ca'], self.fnumerico)
        sheet_libro.write(fila, columna + 2, r['sat_importa_in_ca_iva'], self.fnumerico)
        sheet_libro.write(fila, columna + 3, r['sat_importa_in_ca_total'], self.fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "Importacion Fuera CA")
        sheet_libro.write(fila, columna + 1, r['sat_importa_out_ca'], self.fnumerico)
        sheet_libro.write(fila, columna + 2, r['sat_importa_out_ca_iva'], self.fnumerico)
        sheet_libro.write(fila, columna + 3, r['sat_importa_out_ca_total'], self.fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "Total")
        sheet_libro.write_formula(fila, columna + 1, '=SUM(B2:B7)', self.fnumerico)
        sheet_libro.write(fila, columna + 2, '=SUM(C2:C7)', self.fnumerico)
        sheet_libro.write(fila, columna + 3, '=SUM(D2:D7)', self.fnumerico)

        sheet_libro = self.workbook.add_worksheet("Top 10 " + libro['descripcion'])

        fila = 0
        sheet_libro.set_column(columna,columna,12)
        sheet_libro.set_column(columna + 1,columna + 1,55)
        sheet_libro.set_column(columna + 2,columna + 2,12)
        sheet_libro.set_column(columna + 3,columna + 3,12)


        sheet_libro.write(fila, columna, "Nit", self.bold)
        sheet_libro.write(fila, columna + 1, "Cliente", self.bold)
        sheet_libro.write(fila, columna + 2, "Cantidad", self.bold)
        sheet_libro.write(fila, columna + 3, "Monto Base", self.bold)
        fila = 1
        for t in libro['top10_documentos']:
            sheet_libro.write(fila, columna, t['partner'].vat)
            sheet_libro.write(fila, columna + 1, t['partner'].name)
            sheet_libro.write(fila, columna + 2, t['cant_docs'], self.fnumerico)
            sheet_libro.write(fila, columna + 3, t['sat_base'], self.fnumerico)
            fila += 1

        sheet_libro.write(fila, columna, '')
        sheet_libro.write(fila, columna + 1, 'Diferencia')
        sheet_libro.write(fila, columna + 2, libro['top10_documentos_diferencia']['cant_docs'], self.fnumerico)
        sheet_libro.write(fila, columna + 3, libro['top10_documentos_diferencia']['sat_base'], self.fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "")
        sheet_libro.write(fila, columna + 1, "Total", self.fnumerico)
        sheet_libro.write(fila, columna + 2, libro['top10_documentos_total']['cant_docs'], self.fnumerico)
        sheet_libro.write(fila, columna + 3, libro['top10_documentos_total']['sat_base'], self.fnumerico)


        return sheet_libro

    def generate_xlsx_report(self, workbook, data, data_report):
        self.workbook = workbook
        format1 = workbook.add_format({'font_size': 12, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter', 'bold': True})
        format1.set_align('center')
        self.bold = workbook.add_format({'bold': True})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        self.fnumerico = workbook.add_format({'num_format': '#,##0.00'})
        self.money = workbook.add_format({'font_size': 12, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter', 'bold': True, 'num_format': '#,##0.00','border':0 })
        formato_titulo = workbook.add_format({'bold': 1,'border': 1,'align':'center','valign':'vcenter','fg_color': '#1C1C1C', 'font_color': 'white'})
        formato_resumen = workbook.add_format({'bold': 1,'border': 0,'align':'left','fg_color': '#1C1C1C', 'font_color': 'white'})
        formato_encabezado = workbook.add_format({'bold': 1,'border': 0,'align':'left','fg_color': '#fffff', 'font_color': 'black'})


        libros_fiscales = self.env["report.l10n_gt_sat.librofiscal"].get_libro(data)
        for libro in libros_fiscales:
            vendedor = data['form']['vendedor']
            tipo=data['form']['tipo']

            sheet_libro = workbook.add_worksheet(libro['descripcion'])
            sheet_libro.merge_range('A1:F1', 'GUATEMALA', formato_encabezado)
            sheet_libro.merge_range('A2:F2', self.env.company.company_registry, formato_encabezado)
            sheet_libro.merge_range('A3:F3', "LIBRO DE " + str(libro['descripcion']).upper(), formato_encabezado)
            sheet_libro.merge_range('A4:F4', "DEL " + libro['del'] + " AL " + libro['del'], formato_encabezado)
            sheet_libro.merge_range('A5:F5','Resolucion: {}'.format(data['form']['resolucion'] if data['form']['resolucion'] else ''), formato_encabezado)

            fila = 5
            columna = 0
            if libro['libro'] == 'sale':
                sheet_libro = self._get_libro_ventas(libro, sheet_libro, fila, columna, formato_titulo,formato_resumen, date_format, vendedor,tipo)
            else:
                sheet_libro = self._get_libro_compras(libro, sheet_libro, fila, columna, formato_titulo, date_format,tipo)
