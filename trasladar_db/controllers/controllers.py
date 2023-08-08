# -*- coding: utf-8 -*-
# from odoo import http


# class TrasladarDb(http.Controller):
#     @http.route('/trasladar_db/trasladar_db', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/trasladar_db/trasladar_db/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('trasladar_db.listing', {
#             'root': '/trasladar_db/trasladar_db',
#             'objects': http.request.env['trasladar_db.trasladar_db'].search([]),
#         })

#     @http.route('/trasladar_db/trasladar_db/objects/<model("trasladar_db.trasladar_db"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('trasladar_db.object', {
#             'object': obj
#         })
