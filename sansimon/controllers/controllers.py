# -*- coding: utf-8 -*-
# from odoo import http


# class Sansimon(http.Controller):
#     @http.route('/sansimon/sansimon/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sansimon/sansimon/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sansimon.listing', {
#             'root': '/sansimon/sansimon',
#             'objects': http.request.env['sansimon.sansimon'].search([]),
#         })

#     @http.route('/sansimon/sansimon/objects/<model("sansimon.sansimon"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sansimon.object', {
#             'object': obj
#         })
