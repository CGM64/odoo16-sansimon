# -*- coding: utf-8 -*-

import base64
import io

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.base.models.res_bank import sanitize_account_number
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import logging
_logger = logging.getLogger(__name__)

MESES = ["Unknown",
          "Enero",
          "Febrero",
          "Marzo",
          "April",
          "Mayo",
          "Junio",
          "Julio",
          "Augusto",
          "Septiembre",
          "Octubre",
          "Noviembre",
          "Diciembre"]

class ResBank(models.Model):
    _inherit = "res.bank"

    template_extractos = fields.Selection(selection=[
        ('BAM','Banco Agromercantil'),
        ('BI','Banco Industrial'),
        ('G&T','Banco G&T Continental'),
        ('BANRURAL','BANRURAL'),
        ], string='Plantilla extracto bancario')

class AccountJournal(models.Model):
    _inherit = "account.journal"

    def __get_bank_statements_available_sources(self):
        rslt = super(AccountJournal, self).__get_bank_statements_available_sources()
        rslt.append(("file_import", _("Importacion de archivo csv.")))
        return rslt

class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

    def _parse_file(self, data_file):

        cuenta_bancaria = self.env['account.journal'].browse(self.env.context.get('journal_id'))
        if cuenta_bancaria.currency_id:
            company_currency = cuenta_bancaria.currency_id
        else:
            company_currency = cuenta_bancaria.company_id.currency_id

        def rmspaces(s):
            return " ".join(s.split())



        vals_bank_statement = {}
        saldo_inicial = 0.0
        saldo_final = 0.0

        if cuenta_bancaria.bank_id.template_extractos == 'BAM':
            transactions, anio, mes, saldo_inicial, saldo_final = self._getTransaccionBAM(data_file)
        elif cuenta_bancaria.bank_id.template_extractos == 'BI':
            transactions, anio, mes, saldo_inicial, saldo_final = self._getTransaccionBIM(data_file)
        elif cuenta_bancaria.bank_id.template_extractos == 'G&T':
            transactions, anio, mes, saldo_inicial, saldo_final = self._getTransaccionGYT(data_file)
        elif cuenta_bancaria.bank_id.template_extractos == 'BANRURAL':
            transactions, anio, mes, saldo_inicial, saldo_final = self._getTransaccionBANRURAL(data_file)
        else:
            raise UserError(_("No existe formato configurado para este banco."))


#        raise UserError(_('Could not make sense of the given file.\nDid you install the module to support this type of file ?'))
        referencia = "%s %s" % (MESES[mes], anio)
        vals_bank_statement.update({
            'name': referencia,
            'balance_start': saldo_inicial,
            'balance_end_real': saldo_final,
            'transactions': transactions
        })
        currency_code = company_currency.name
        acc_number = cuenta_bancaria.bank_acc_number
        return currency_code, acc_number, [vals_bank_statement]

    def _getTransaccionGYT(self,data_file):
        recordlist = data_file.decode('windows-1252').split(u'\n')
        transactions = []
        vals_line = {'name': []}
        total = 0.0
        info = {}
        mes = None
        anio = None
        saldo_final = saldo_inicial = detalle = 0
        numeros = ['1','2','3','4','5','6','7','8','9','0']
        for line in recordlist:
            vals_line = {}
            if 'Fecha:' in line:
                linea = line.split(' ')
                mes = int(MESES.index(linea[len(linea)-2]))
                anio = int(linea[len(linea)-1])

            if 'Saldo Final:' in line:
                saldo_final = line.split(' ')
                saldo_final = saldo_final[len(saldo_final)-1].replace(',','')

            if 'Saldo al inicio del mes:' in line:
                saldo_inicial = line.split(' ')
                saldo_inicial = saldo_inicial[len(saldo_inicial)-1].replace(',','')

            if detalle == 1:
                l = str(line)
                if not l[0] in numeros:
                    detalle = 0
                else:
                    fecha = str(line[info['columna_fecha']:info['columna_docto']-1]).replace(' ','')
                    fecha = datetime.strptime(fecha, '%d/%m/%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)
                    vals_line['sequence'] = len(transactions) + 1
                    vals_line['date'] = fecha
                    vals_line['name'] = '{} : {}'.format(line[info['columna_docto']:info['columna_descripcion']-1],line[info['columna_descripcion']:info['columna_debito']-2])
                    vals_line['ref'] = line[info['columna_docto']:info['columna_descripcion']-1]
                    debe = line[info['columna_debito']:info['columna_credito']-1]
                    haber = line[info['columna_credito']:info['columna_saldo']]
                    debe = debe.replace(',','').replace(' ','')
                    haber = haber.replace(',','').replace(' ','')
                    debe = 0.0 if debe == '' else debe
                    haber = 0.0 if haber == '' else haber
                    vals_line['amount'] = float(debe) + float(haber)
                    transactions.append(vals_line)


            if 'Fecha' in line and 'Docto' in line and 'Descripcion' in line:
                encabezado = str(line)
                detalle = 1
                info['columna_fecha'] = encabezado.find('Fecha')
                info['columna_docto'] = encabezado.find('Docto')
                info['columna_descripcion'] = encabezado.find('Descripcion')
                info['columna_debito'] = encabezado.find('Debito')-1
                info['columna_credito'] = encabezado.find('Credito')
                info['columna_saldo'] = encabezado.find('Saldo')
                info['columna_agencia'] = encabezado.find('Agencia') + 1

        return transactions, anio, mes, saldo_inicial, saldo_final


    def _getTransaccionBIM(self, data_file):
        recordlist = data_file.decode('windows-1252').split(u'\n')
        transactions = []
        vals_line = {'name': []}
        total = 0.0

        encabezado = True
        saldo_inicial = 0.0
        saldo_final = 0.0
        primera_linea = True
        segunda_linea = True
        fecha_primera_linea = None
        mes = None
        anio = None
        numero_linea = 0
        for line in recordlist:
            numero_linea += 1
            if not line.strip():
                continue
            if numero_linea > 9:
                vals_line = {}
                nueva_linea = line.split(',')
                vals_line['sequence'] = len(transactions) + 1
                vals_line['date'] = datetime.strptime(nueva_linea[0], '%d-%m-%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)
                vals_line['name'] = nueva_linea[1] + ": " + nueva_linea[2]+ ' ' + nueva_linea[3]
                vals_line['ref'] = nueva_linea[2]
                debe = nueva_linea[5] if nueva_linea[5] else "0.0"
                haber = nueva_linea[4] if nueva_linea[4] else "0.0"
                vals_line['amount'] = float(debe) - float(haber)
                fecha_primera_linea = vals_line['date']

                if primera_linea:
                    saldo_inicial = float(nueva_linea[6]) - vals_line['amount']
                    fecha_primera_linea = datetime.strptime(fecha_primera_linea, DEFAULT_SERVER_DATE_FORMAT)
                    mes = fecha_primera_linea.month
                    anio = fecha_primera_linea.year
                    primera_linea = False
                saldo_final = nueva_linea[6]
                transactions.append(vals_line)

        return transactions, anio, mes, saldo_inicial, saldo_final

    def _getTransaccionBAM(self, data_file):

        recordlist = data_file.decode('windows-1252').split(u'\n')
        transactions = []
        vals_line = {'name': []}
        total = 0.0

        encabezado = True
        saldo_inicial = 0.0
        saldo_final = 0.0
        segunda_linea = True
        fecha_primera_linea = None
        mes = None
        anio = None
        for line in recordlist:
            if encabezado:
                encabezado = False
            else:
                vals_line = {}
                nueva_linea = line.split(',')

                if not line:
                    continue
                vals_line['sequence'] = len(transactions) + 1
                vals_line['date'] = datetime.strptime(nueva_linea[0], '%d/%m/%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)
                if nueva_linea[4] == "CHEQUE PAGADO":
                    vals_line['name'] = nueva_linea[4] + ": " + str(nueva_linea[3])+ " " +str(nueva_linea[2])[-4:]
                else:
                    vals_line['name'] = nueva_linea[4] + ": " + str(nueva_linea[3])+ " " +str(nueva_linea[2])[-4:]
                vals_line['ref'] = nueva_linea[2]
                vals_line['amount'] = float(nueva_linea[6]) - float(nueva_linea[7])
                if segunda_linea:
                    segunda_linea = False
                    saldo_inicial = float(nueva_linea[8]) - vals_line['amount']
                    fecha_primera_linea = vals_line['date']
                    if fecha_primera_linea:
                            fecha_primera_linea = datetime.strptime(fecha_primera_linea, DEFAULT_SERVER_DATE_FORMAT)
                            mes = fecha_primera_linea.month
                            anio = fecha_primera_linea.year

                saldo_final = nueva_linea[8]

                transactions.append(vals_line)
        return transactions, anio, mes, saldo_inicial, saldo_final


    def _getTransaccionBANRURAL(self, data_file):

        recordlist = data_file.decode('windows-1252').split(u'\n')
        transactions = []
        vals_line = {'name': []}
        total = 0.0

        encabezado = False
        saldo_inicial = 0.0
        saldo_final = 0.0
        segunda_linea = True
        fecha_primera_linea = None
        mes = None
        anio = None
        sign = 1

        for line in recordlist:
            if encabezado:
                encabezado = False
            else:
                vals_line = {}
                nueva_linea = line.split(';')

                if not line:
                    continue
                sign = 1 if nueva_linea[4] == 'C' else -1
                vals_line['sequence'] = len(transactions) + 1
                vals_line['date'] = datetime.strptime(nueva_linea[0], '%d/%m/%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)
                vals_line['name'] = nueva_linea[2] + ": " + str(nueva_linea[3])
                vals_line['ref'] = nueva_linea[10]
                vals_line['amount'] = float(nueva_linea[5].replace(",","")) * sign
                if segunda_linea:
                    segunda_linea = False
                    saldo_inicial = float(nueva_linea[6].replace(",","")) - (vals_line['amount'])
                    fecha_primera_linea = vals_line['date']
                    if fecha_primera_linea:
                            fecha_primera_linea = datetime.strptime(fecha_primera_linea, DEFAULT_SERVER_DATE_FORMAT)
                            mes = fecha_primera_linea.month
                            anio = fecha_primera_linea.year

                saldo_final = nueva_linea[6].replace(",","")

                transactions.append(vals_line)
        return transactions, anio, mes, saldo_inicial, saldo_final
