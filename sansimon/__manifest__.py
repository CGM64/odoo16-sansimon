# -*- coding: utf-8 -*-
{
    'name': "San Simon",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com """,

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
    'depends': ['account','stock','connect_mssql','l10n_gt','stock_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_report.xml',
        'views/account_journal_view.xml',
        'wizard/catalogo_excel_wizard_view.xml',
        'wizard/stock_move_periodo_wizard_view.xml',
        'report/report_invoice.xml',
        'report/report_invoice_ticket.xml',
        'data/account.account.template.csv',
        'data/ir_cron_data.xml',
        'data/account_account_data.xml',
        #'data/stock_account_data.xml',
        'report/sale_order.xml',
        'report/sale_order_templates.xml',
        'report/stock_picking_report.xml',
        'views/sale_order_line.xml',
        'views/account_move_line.xml',
        'data/sale_group_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
