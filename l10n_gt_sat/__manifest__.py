# -*- coding: utf-8 -*-
{
    'name': "l10n_gt_sat",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Integratec",
    'website': "http://www.integratec.com.gt",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_tax_python','report_xlsx','stock','account_reports','purchase_stock','sale_stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/account_chart_template_data.xml',
        'data/account_account_data.xml',
        'data/stock_account_data.xml',
        'data/res_group_data.xml',
        'data/sequence_res_partner_data.xml',
        #'data/product_dai_data.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/account_report.xml',
        'views/account_move_views.xml',
        'views/account_account_views.xml',
        'views/account_tax.xml',
        'views/account_journal_view.xml',
        'views/product_template_view.xml',
        'views/report_libro_diario.xml',
        'views/stock_piking_view.xml',
        'views/purchase_order_views.xml',
        'views/account_payment_view.xml',
        'report/check_account_payment.xml',
        'wizard/account_report_libros_view.xml',
        'wizard/account_report_importacion.xml',
        'wizard/libro_contable_view.xml',
        'wizard/importacion_contabilidad.xml',
        'report/account_librofiscal_report_view.xml',
        'report/purchase_order_views.xml',
        'views/res_company.xml',
        'views/report_invoice.xml',
        'views/sale_view.xml',
        'views/res_partner_view.xml',
        'views/custom_view.xml',
        'wizard/tags_view.xml',
        'report/purchase_order_views.xml',
        'views/res_currency_views.xml',
        'views/sale_order_view.xml',
        'views/res_municipio_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',

    ],
}
