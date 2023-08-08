# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons.l10n_gt_sat.wizard import account_report_libros
import calendar

TIPOS_DE_LIBROS = account_report_libros.TIPOS_DE_LIBROS

class AccountCommonJournalReport(models.TransientModel):
    _name = 'report.l10n_gt_sat.librofiscal'
    _description = 'Libro Fiscal Report'


    amount_currency = fields.Boolean('With Currency', help="Print Report with the currency column if the currency differs from the company currency.")

    #Funcion que me devuelve la lista de los libros a procesar
    def _get_tipo_libro(self, libro):
        list_tipo_libro = []
        for tipo_libro in TIPOS_DE_LIBROS:
            dict_libro = {}
            dict_libro['libro'] = tipo_libro[0]
            dict_libro['descripcion'] = tipo_libro[1]
            if tipo_libro[0] not in ['all'] and tipo_libro[0] == libro:
                list_tipo_libro = []
                list_tipo_libro.append(dict_libro)
                return list_tipo_libro
            elif tipo_libro[0] not in ['all']:
                list_tipo_libro.append(dict_libro)

        return list_tipo_libro

    def _get_libros_procesar(self, data):
        libro = data['form']['libro']
        libros_fiscales = self._get_tipo_libro(libro)

        return libros_fiscales



    #Funcion que devuelve el arreglo listo para procesar en el reportes
    def get_libro(self, data):
        company_id = data['form']['company_id'][0]
        
        #sale
        #purchase
        libros = self._get_libros_procesar(data)

        libro_fiscal = []
        ejercicio = int(data['form']['ejercicio'])
        periodo = int(data['form']['periodo'])

        ultimo_diadelmes = calendar.monthrange(ejercicio, periodo)[1]
        fecha_del = '%s-%s-01' % (ejercicio, periodo)
        fecha_al = '%s-%s-%s' % (ejercicio, periodo, ultimo_diadelmes)

        for libro in libros:
            journals = self.env['account.journal'].search([('invoice_receipt','=',True),('type', '=', libro['libro']),('company_id', '=', company_id)])
            print("#####=====")
            print(company_id)
            print(libro['libro'])
            print(journals)
            tipo_libro = {}
            tipo_libro['tipo'] = data['form']['tipo']
            tipo_libro['libro'] = libro['libro']
            tipo_libro['descripcion'] = libro['descripcion']
            tipo_libro['del'] = '01/%s/%s' % (periodo, ejercicio)
            tipo_libro['al'] = '%s/%s/%s' % (ultimo_diadelmes, periodo, ejercicio)
            no_linea = 0
            facturas = []
            libro_resumido = {}

            concepto_iva = {}
            concepto_iva['servicio'] = concepto_iva['servicio_iva'] = 0.0
            concepto_iva['bien'] = concepto_iva['bien_iva'] = 0.0
            concepto_iva['sat_combustible'] = concepto_iva['sat_combustible_iva'] = 0.0
            concepto_iva['sat_iva_total'] = concepto_iva['sat_subtotal_total'] = 0.0
            concepto_iva['amount_total_total'] = concepto_iva['sat_peq_contri'] = 0.0
            concepto_iva['sat_exento'] = concepto_iva['sat_base'] = 0.0
            concepto_iva['sat_importa_in_ca'] = concepto_iva['sat_importa_in_ca_iva'] = 0.0
            concepto_iva['sat_importa_out_ca'] = concepto_iva['sat_importa_out_ca_iva'] = 0.0
            concepto_iva['sat_exportacion_in_ca'] = 0

            lista_top_documentos = {}
            cantidad_documentos,cantidad_facturas,cantidad_notas_credito,total_notas_credito=0,0,0,0
            for journal in journals:
                domain = [
                    ('company_id', '=', company_id),
                    ('journal_id', '=', journal.id),
                    ('date','>=',fecha_del),
                    ('date','<=',fecha_al),
                    ('invoice_date','!=',False),
                    ('state','in',('posted','cancel')),
                    #('partner_id','=',11151),
                    #('id','=',33202),
                ]
                if libro['libro'] == "sale":
                    domain.append(('fel_firma','!=',False))
                if libro['libro'] == "purchase":
                    domain.append(('state', '=', 'posted'))
                documentos = self.env['account.move'].search(domain).sorted(key=lambda r: (r.invoice_date, r.id))

                for documento in documentos:
                    cantidad_documentos+=1

                    no_linea += 1
                    documento.no_linea = no_linea
                    facturas.append(documento)

                    #Comienza desarrollo para el resumen por concepto
                    concepto_iva['servicio'] += documento.sat_servicio
                    concepto_iva['bien'] += documento.sat_bien
                    concepto_iva['sat_peq_contri'] += documento.sat_peq_contri
                    concepto_iva['sat_exento'] += documento.sat_exento
                    concepto_iva['sat_combustible'] += documento.sat_combustible
                    concepto_iva['sat_base'] += documento.sat_base
                    concepto_iva['sat_importa_in_ca'] += documento.sat_importa_in_ca
                    concepto_iva['sat_importa_out_ca'] += documento.sat_importa_out_ca
                    concepto_iva['sat_exportacion_in_ca'] += documento.sat_exportacion_in_ca

                    if documento.sat_servicio != 0:
                        concepto_iva['servicio_iva'] += documento.sat_iva
                    if documento.sat_bien != 0:
                        concepto_iva['bien_iva'] += documento.sat_iva
                    if documento.sat_combustible != 0:
                        concepto_iva['sat_combustible_iva'] += documento.sat_iva
                    if documento.sat_importa_in_ca != 0:
                        concepto_iva['sat_importa_in_ca_iva'] = documento.sat_iva
                    if documento.sat_importa_out_ca != 0:
                        concepto_iva['sat_importa_out_ca_iva'] =  documento.sat_iva

                    concepto_iva['sat_subtotal_total'] += documento.sat_subtotal
                    concepto_iva['sat_iva_total'] += documento.sat_iva
                    concepto_iva['amount_total_total'] += documento.sat_amount_total


                    top_key = documento.partner_id.id

                    #Comienza el desarrollo para top 10
                    if documento.journal_id.tipo_operacion not in ('DUCA_IN','DUCA_OUT'):
                        dic_top_documento = {}
                        dic_top_documento['partner_id'] = documento.partner_id.id
                        dic_top_documento['partner'] = documento.partner_id

                        #Primero analice si la lista del top existe, si existe lo reasigno y si no lo inicializo con valor 0, para que se pueda hacer la suma
                        if top_key in lista_top_documentos:
                            dic_top_documento = lista_top_documentos[top_key]
                        else:
                            dic_top_documento['sat_base'] = 0.0
                            dic_top_documento['cant_docs'] = 0

                        dic_top_documento['sat_base'] = dic_top_documento['sat_base'] + documento.sat_combustible + documento.sat_servicio + documento.sat_bien + documento.sat_importa_in_ca + documento.sat_importa_out_ca
                        dic_top_documento['cant_docs'] = dic_top_documento['cant_docs'] + 1
                        lista_top_documentos[top_key] = dic_top_documento

                    #Comienza el desarrollo para el libro resumido
                    day_to_year = documento.invoice_date.timetuple().tm_yday #Obtengo el dia del anio para utilizarlo como llave

                    libro_resumido_linea = {}
                    dia_documento="{}_{}".format(documento.journal_id.code,day_to_year)
                    libro_resumido_linea['no_linea'] = 0
                    libro_resumido_linea['codigo'] = documento.journal_id.code
                    libro_resumido_linea['dia'] = documento.invoice_date
                    # libro_resumido_linea['fecha'] = documento.invoice_date.strftime('%d/%m/%Y')

                    #SUMA POR TIPO DE DOCUMENTO
                    if documento.journal_id.tipo_documento in ['NDEB','NCRE']:
                        cantidad_notas_credito+=1
                        total_notas_credito+=documento.amount_total
                    else:
                        cantidad_facturas+=1
                        

                    if dia_documento in libro_resumido:
                        libro_resumido_linea = libro_resumido[dia_documento]
                    else:
                        libro_resumido_linea['total_documentos'] = 0
                        libro_resumido_linea['sat_servicio'] = 0.0
                        libro_resumido_linea['sat_bien'] = 0.0
                        libro_resumido_linea['sat_subtotal'] = 0.0
                        libro_resumido_linea['sat_iva'] = 0.0
                        libro_resumido_linea['sat_amount_total'] = 0.0
                        libro_resumido_linea['sat_peq_contri'] = 0.0
                        libro_resumido_linea['sat_exento'] = 0.0
                        libro_resumido_linea['sat_combustible'] = 0.0
                        libro_resumido_linea['sat_base'] = 0.0
                        libro_resumido_linea['sat_importa_in_ca'] = 0.0
                        libro_resumido_linea['sat_importa_out_ca'] = 0.0

                    libro_resumido_linea['total_documentos'] = libro_resumido_linea['total_documentos'] + 1
                    libro_resumido_linea['sat_servicio'] = libro_resumido_linea['sat_servicio'] + documento.sat_servicio
                    libro_resumido_linea['sat_importa_in_ca'] = libro_resumido_linea['sat_importa_in_ca'] + documento.sat_importa_in_ca
                    libro_resumido_linea['sat_importa_out_ca'] = libro_resumido_linea['sat_importa_out_ca'] + documento.sat_importa_out_ca
                    libro_resumido_linea['sat_peq_contri'] = libro_resumido_linea['sat_peq_contri'] + documento.sat_peq_contri
                    libro_resumido_linea['sat_bien'] = libro_resumido_linea['sat_bien'] + documento.sat_bien
                    libro_resumido_linea['sat_subtotal'] = libro_resumido_linea['sat_subtotal'] + documento.sat_subtotal
                    libro_resumido_linea['sat_iva'] = libro_resumido_linea['sat_iva'] + documento.sat_iva
                    libro_resumido_linea['sat_amount_total'] = libro_resumido_linea['sat_amount_total'] + documento.sat_amount_total
                    libro_resumido_linea['sat_exento'] = libro_resumido_linea['sat_exento'] + documento.sat_exento
                    libro_resumido_linea['sat_combustible'] = libro_resumido_linea['sat_combustible'] + documento.sat_combustible
                    libro_resumido_linea['sat_base'] = libro_resumido_linea['sat_base'] + documento.sat_base
                    libro_resumido[dia_documento] = libro_resumido_linea


            concepto_iva['cantidad_documentos'] =cantidad_documentos
            concepto_iva['cantidad_facturas'] =cantidad_facturas
            concepto_iva['cantidad_notas_credito'] =cantidad_notas_credito
            concepto_iva['total_notas_credito'] =total_notas_credito

            concepto_iva['servicio_total'] = concepto_iva['servicio'] +  concepto_iva['servicio_iva']
            concepto_iva['bien_total'] = concepto_iva['bien'] +  concepto_iva['bien_iva']
            concepto_iva['sat_combustible_total'] = concepto_iva['sat_combustible'] +  concepto_iva['sat_combustible_iva']
            concepto_iva['sat_importa_in_ca_total'] = concepto_iva['sat_importa_in_ca'] +  concepto_iva['sat_importa_in_ca_iva']
            concepto_iva['sat_importa_out_ca_total'] = concepto_iva['sat_importa_out_ca'] +  concepto_iva['sat_importa_out_ca_iva']

            concepto_iva['sat_total_general_base'] = concepto_iva['servicio'] + concepto_iva['bien'] + concepto_iva['sat_peq_contri'] + concepto_iva['sat_combustible'] + concepto_iva['sat_importa_in_ca'] + concepto_iva['sat_importa_out_ca']
            concepto_iva['sat_total_general_iva'] = concepto_iva['servicio_iva'] + concepto_iva['bien_iva'] + concepto_iva['sat_combustible_iva'] + concepto_iva['sat_importa_in_ca_iva'] + concepto_iva['sat_importa_out_ca_iva']
            concepto_iva['sat_total_general'] = concepto_iva['sat_total_general_base'] + concepto_iva['sat_total_general_iva']

            tipo_libro['facturas'] = facturas
            prueba = sorted(libro_resumido.items())
            tipo_libro['resumido'] = prueba
            # print(prueba)

            

            tipo_libro['resumen'] = concepto_iva
            #tipo_libro['top_documentos'] = sorted(lista_top_documentos.items(), key = lambda kv:kv[1]['sat_servicio'], reverse = True)[:10]
            lista_top_documentos = sorted(lista_top_documentos.items(), key = lambda kv:kv[1]['sat_base'], reverse = True)
            #Se requiere generar una nueva lista, con el top 10 de proveedores, y el resto meterno en un proveedor diferencia
            lista_top10_documentos = []
            lista_top10_documentos_diferencia = {}
            lista_top10_documentos_sum_base = 0.0
            lista_top10_documentos_sum_docs = 0
            #variables de totales
            lista_top10_documentos_total = {}
            lista_top10_documentos_total_base = 0.0
            lista_top10_documentos_total_docs = 0
            i = 0
            for prov in lista_top_documentos:
                if i < 10:
                    lista_top10_documentos.append(prov[1])
                else:
                    lista_top10_documentos_sum_base += prov[1]['sat_base']
                    lista_top10_documentos_sum_docs += prov[1]['cant_docs']
                lista_top10_documentos_total_base += prov[1]['sat_base']
                lista_top10_documentos_total_docs += prov[1]['cant_docs']

                i += 1
            lista_top10_documentos_diferencia = {
                'name': 'Otras Facturas',
                'sat_base': lista_top10_documentos_sum_base,
                'cant_docs': lista_top10_documentos_sum_docs,
            }
            lista_top10_documentos_total = {
                'name': 'Total',
                'sat_base': lista_top10_documentos_total_base,
                'cant_docs': lista_top10_documentos_total_docs,
            }

            tipo_libro['top_documentos'] = lista_top_documentos
            tipo_libro['top10_documentos'] = lista_top10_documentos
            tipo_libro['top10_documentos_diferencia'] = lista_top10_documentos_diferencia
            tipo_libro['top10_documentos_total'] = lista_top10_documentos_total
            libro_fiscal.append(tipo_libro)
            # print(tipo_libro)


        # print('libro_fiscal',libro_fiscal)
        return libro_fiscal

        #docs = self.env['account.move'].search([('journal_id', '=', journal.id)], limit=1):


    @api.model
    def _get_report_values(self,docids,data):

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        libros = self.get_libro(data)
        libro_fiscal = self.env['l10n_gt_sat.librofiscal.report'].search([('id','=',data['context']['active_id'])])
        # print("llego al get libro")



        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'libros': libros,
            'currency': self.env.company.currency_id,
            'modelo': libro_fiscal,
        }

        return docargs
