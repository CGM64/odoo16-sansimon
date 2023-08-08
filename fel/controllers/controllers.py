# -*- coding: utf-8 -*-
from odoo import http

# class Fel(http.Controller):
#     @http.route('/fel/fel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fel/fel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fel.listing', {
#             'root': '/fel/fel',
#             'objects': http.request.env['fel.fel'].search([]),
#         })

#     @http.route('/fel/fel/objects/<model("fel.fel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fel.object', {
#             'object': obj
#         })