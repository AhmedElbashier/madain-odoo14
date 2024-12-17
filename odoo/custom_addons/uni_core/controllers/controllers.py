# -*- coding: utf-8 -*-
from odoo import http

# class UniCore(http.Controller):
#     @http.route('/uni_core/uni_core/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/uni_core/uni_core/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('uni_core.listing', {
#             'root': '/uni_core/uni_core',
#             'objects': http.request.env['uni_core.uni_core'].search([]),
#         })

#     @http.route('/uni_core/uni_core/objects/<model("uni_core.uni_core"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('uni_core.object', {
#             'object': obj
#         })