# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = "account.journal"

    tipo_operacion = fields.Selection([
        ('FACT', 'Factura'),
        ('EXPO', 'Exportacion'),
        ('IMPO', 'Importacion'),
        ('DUCA_IN', 'Duca IN CA'),
        ('DUCA_OUT', 'Duca OUT CA'),
    ],
    string='Tipo de Documento',
    help="Indica el tipo de documento.")
    tipo_documento = fields.Selection([
                ('FACT', 'Factura'),
                ('FCAM', 'Factura Cambiaria'),
                ('FPEQ', 'Factura Pequeño Contribuyente'),
                ('FCAP', 'Factura Cambiaria Pequeño Contribuyente'),
                ('FESP', 'Factura Especial'),
                ('NABN', 'Nota de Abono'),
                ('RDON', 'Recibo por donación'),
                ('RECI', 'Recibo'),
                ('NDEB', 'Nota de Débito'),
                ('NCRE', 'Nota de Crédito'),
                ('FACA', 'Factura Contribuyente Agropecuario'),
                ('FCCA', 'Factura Cambiaria Contribuyente Agropecuario'),
                ('FAPE', 'Factura Pequeño Contribuyente Régimen Electrónico'),
                ('FCPE', 'Factura Cambiaria Pequeño Contribuyente Régimen Electrónico'),
                ('FAAE', 'Factura Contribuyente AgropecuarioRégimen Electrónico Especial'),
                ('FCAE', 'Factura Cambiaria Contribuyente AgropecuarioRégimen Electrónico Especial'),
            ],
            string='Tipo de DTE',
            help="Indica el tipo de DTE que se utilizara en el diario.")
    afiliacion_iva = fields.Selection([
                ('GEN', 'General'),
                ('EXE', 'Exento'),
                ('PEQ', 'Pequeño Contribuyente'),
            ],
            string='Afiliacion IVA',
            help="De acuerdo al Régimen que tenga registrado el contribuyente, se refiere a que puede ser General/Exento o Pequeño Contribuyente.")
    invoice_receipt  = fields.Boolean(string='Incluir en Libros Fiscales', default=False)

    voucher_template = fields.Selection(selection=[
            ('l10n_gt_sat.voucher_1', 'Plantilla Voucher 1'),
            ('l10n_gt_sat.voucher_2', 'Plantilla Voucher 2'),
            ('l10n_gt_sat.voucher_3', 'Plantilla Voucher 3'),
        ], string='Plantilla Voucher', default='l10n_gt_sat.voucher_1')

    cheque_template = fields.Selection(selection=[
            ('l10n_gt_sat.ckgt_check_BAM', 'Plantilla Cheque BAM'),
            ('l10n_gt_sat.ckgt_check_BI', 'Plantilla Cheque BI'),
            ('l10n_gt_sat.ckgt_check_GYT', 'Plantilla Cheque GYT'),
            ('l10n_gt_sat.ckgt_check_BAC', 'Plantilla Cheque BAC'),
        ], string='Platilla Cheque', default='l10n_gt_sat.ckgt_check_BAM')

    papel_cheque = fields.Selection(selection=[
            ('l10n_gt_sat.report_payment_receipt_media', 'Papel Media Carta'),
            ('l10n_gt_sat.report_payment_receipt_carta', 'Papel Carta'),
            ('l10n_gt_sat.report_payment_papel_cheque', 'Papel Cheque'),
        ], string='Papel', default='l10n_gt_sat.report_payment_receipt_media')
    invoice_name = fields.Char(string='Nombre en reporte',default='Factura',help='Nombre que aparece en reporte de factura')
