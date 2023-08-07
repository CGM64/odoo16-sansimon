# -*- coding: utf-8 -*-
# from odoo import http


# class AccountBankStatementGtImport(http.Controller):
#     @http.route('/account_bank_statement_gt_import/account_bank_statement_gt_import', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_bank_statement_gt_import/account_bank_statement_gt_import/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_bank_statement_gt_import.listing', {
#             'root': '/account_bank_statement_gt_import/account_bank_statement_gt_import',
#             'objects': http.request.env['account_bank_statement_gt_import.account_bank_statement_gt_import'].search([]),
#         })

#     @http.route('/account_bank_statement_gt_import/account_bank_statement_gt_import/objects/<model("account_bank_statement_gt_import.account_bank_statement_gt_import"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_bank_statement_gt_import.object', {
#             'object': obj
#         })
