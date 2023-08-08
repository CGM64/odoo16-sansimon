# -*- coding: utf-8 -*-

import calendar
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from odoo import api, fields, models, _



class AnalisisImportacionesContabilidad(models.TransientModel):
    _name = "l10n_gt_sat.importacion.contabilidad"
    _description = "Analisis de Importacion y Contabilidad"
    
    previous_month = datetime.today() + relativedelta(months=-1)
    days_previous_month = calendar.monthrange(previous_month.year, previous_month.month)

    fecha_inicio = fields.Date(string='Fecha Inicio', required=True, default=previous_month.strftime('%Y-%m-01'))
    fecha_fin = fields.Date(string='Fecha Fin', required=True, default=previous_month.strftime('%Y-%m-' + str(days_previous_month[1])))

    def export_xls(self):
        self.ensure_one()
        data = {}
        data['form'] = self.read(['fecha_inicio', 'fecha_fin'])[0]
        return self.env['ir.actions.report'].search([('report_name', '=', 'l10n_gt_sat.analisis_importacion_contabilidad_report_xls'),
                ('report_type', '=', 'xlsx')], limit=1).report_action(self,data=data)
        

class AnalisisImportacionesContabilidadXls(models.AbstractModel):
    _name = 'report.l10n_gt_sat.analisis_importacion_contabilidad_report_xls'
    _description = 'Analisis de Importaciones y Contabilidad XLS'
    _inherit = 'report.report_xlsx.abstract'

    workbook = None

    def generate_xlsx_report(self, workbook, data, data_report):
        self.workbook = workbook
        sheet_libro = workbook.add_worksheet('Ventas')
        money = workbook.add_format({'align':'right','valign':'vcenter','num_format': 'Q#,##0.00'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy','align':'left'})
        izquierda = workbook.add_format({'align':'left','valign':'vcenter','text_wrap':1})
        negritaizquierda = workbook.add_format({'bold': True,'align':'left','valign':'vcenter','text_wrap':1})
        porcentaje = workbook.add_format({'num_format': '0.00%','align':'left'})

        i = 0
        
        sheet_libro.set_column(0,0,5)
        sheet_libro.set_column(1,1,15)
        sheet_libro.set_column(2,2,10)
        sheet_libro.set_column(3,3,35)
        sheet_libro.set_column(4,4,25)
        sheet_libro.set_column(5,5,20)
        sheet_libro.set_column(6,6,20)
        sheet_libro.set_column(7,7,20)
        sheet_libro.set_column(8,8,10)
        sheet_libro.set_column(9,9,35)
        sheet_libro.set_column(10,10,20)
        sheet_libro.set_column(11,11,20)
        
        sheet_libro.write(i,0,"No", negritaizquierda)
        sheet_libro.write(i,1,"Destino", negritaizquierda)
        sheet_libro.write(i,2,"Fecha", negritaizquierda)
        sheet_libro.write(i,3,"Contabilidad", negritaizquierda)
        sheet_libro.write(i,4,"Cuenta", negritaizquierda)
        sheet_libro.write(i,5,"Debe", negritaizquierda)
        sheet_libro.write(i,6,"Haber", negritaizquierda)
        sheet_libro.write(i,7,"Pedido", negritaizquierda)
        sheet_libro.write(i,8,"# Fact.", negritaizquierda)
        
        inicio = data['form']['fecha_inicio']
        fin = data['form']['fecha_fin']
        
        #costos_destino = self.env["stock.landed.cost"].search([('id','=',49)])
        costos_destino = self.env["stock.landed.cost"].search([])
        i+=1
        for costo_destino in costos_destino:

            
            contabilidad = costo_destino.account_move_id
            
            #for conta_line in contabilidad.line_ids.filtered(lambda detalle: detalle.account_id.code == '1.1.06.40'):
            for conta_line in contabilidad.line_ids:
                sheet_libro.write(i,0,i)
                sheet_libro.write(i,1,costo_destino.name)
                sheet_libro.write(i,2,costo_destino.date,date_format)                
                sheet_libro.write(i,3,conta_line.name)
                sheet_libro.write(i,4,conta_line.account_id.display_name)
                sheet_libro.write(i,5,conta_line.debit,money)
                sheet_libro.write(i,6,conta_line.credit,money)
                i+=1
            
            pickings = costo_destino.picking_ids
            
            picking_ids = pickings.filtered(lambda l: l.picking_type_id.code == 'incoming')
            
            pedido_compra = None
                
            for picking_id in picking_ids:
                pedido_compra = picking_id.purchase_id
                
                
                
            facturas = pedido_compra.order_line.invoice_lines.move_id.filtered(lambda r: r.type in ('in_invoice', 'in_refund'))
            count_factura = len(facturas)
            #sheet_libro.write(i,8,count_factura) #NUmero de facturas
            
            duca = facturas.sat_invoice_id
            
            facturas_duca = duca.sat_invoice_child_ids
            
            for factura_linea_duca in duca.line_ids:
                sheet_libro.write(i,0,i)
                sheet_libro.write(i,1,costo_destino.name)
                sheet_libro.write(i,2,factura_linea_duca.move_id.date,date_format)
                sheet_libro.write(i,3,factura_linea_duca.move_id.name)
                sheet_libro.write(i,4,factura_linea_duca.account_id.display_name)
                sheet_libro.write(i,5,factura_linea_duca.debit,money)
                sheet_libro.write(i,6,factura_linea_duca.credit,money)
                sheet_libro.write(i,7,"DUCA")
                i+=1              
            
            for factura_detalle in facturas_duca.line_ids:
                sheet_libro.write(i,0,i)
                sheet_libro.write(i,1,costo_destino.name)
                sheet_libro.write(i,2,factura_detalle.move_id.date,date_format)
                sheet_libro.write(i,3,factura_detalle.move_id.name)
                sheet_libro.write(i,4,factura_detalle.account_id.display_name)
                sheet_libro.write(i,5,factura_detalle.debit,money)
                sheet_libro.write(i,6,factura_detalle.credit,money)
                sheet_libro.write(i,7,factura_detalle.purchase_line_id.order_id.name)            
                i+=1
                
                
        