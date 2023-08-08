# -*- coding: utf-8 -*-
{
    'name': "Factura Electrónica FEL",

    'summary': """
        Factura Electrónica en Línea
        """,

    'description': """
        El proceso de Factura Electrónica en Línea se conforma de una serie de procedimientos, para la emisión, transmisión, certificación conservación, por medios electrónicos de facturas, notas de crédito y débito, recibos, y otros documentos autorizados por la Superintendencia de Administración Tributaria para el Régimen FEL, que se denominaran Documentos Tributarios Electrónicos, definiendo sus características y su funcionamiento. Las disposiciones administrativas que regulan la Factura Electrónica en Línea fueron emitidas por medio del Acuerdo del Directorio de la SAT 13-2018 y faculta al Superintendente a establecer por medio de las dependencias competentes, los procedimientos, especificaciones generales y técnicas que permitan implementar el proceso.
    """,

    'author': "Integratec",
    'website': "http://www.integratec.com.gt",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','l10n_gt_sat'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/account_journal_view.xml',
        'views/account_move_view.xml',
        'views/fel_setting_view.xml',
        'views/res_partner_view.xml',
        'data/fel_tipo_frases_data.xml',
        'data/fel_escenario_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
