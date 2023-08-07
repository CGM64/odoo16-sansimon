# -*- coding: utf-8 -*-
# from odoo import http


# class CorteCaja(http.Controller):
#     @http.route('/corte_caja/corte_caja/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/corte_caja/corte_caja/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('corte_caja.listing', {
#             'root': '/corte_caja/corte_caja',
#             'objects': http.request.env['corte_caja.corte_caja'].search([]),
#         })

#     @http.route('/corte_caja/corte_caja/objects/<model("corte_caja.corte_caja"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('corte_caja.object', {
#             'object': obj
#         })
