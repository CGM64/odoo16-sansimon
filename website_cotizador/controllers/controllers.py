# -*- coding: utf-8 -*-
# from odoo import http


# class WebsiteCotizador(http.Controller):
#     @http.route('/website_cotizador/website_cotizador', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_cotizador/website_cotizador/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_cotizador.listing', {
#             'root': '/website_cotizador/website_cotizador',
#             'objects': http.request.env['website_cotizador.website_cotizador'].search([]),
#         })

#     @http.route('/website_cotizador/website_cotizador/objects/<model("website_cotizador.website_cotizador"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_cotizador.object', {
#             'object': obj
#         })
