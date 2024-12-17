# -*- coding: utf-8 -*-
from odoo import http

# class UniHealthService(http.Controller):
#     @http.route('/uni_health_service/uni_health_service/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/uni_health_service/uni_health_service/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('uni_health_service.listing', {
#             'root': '/uni_health_service/uni_health_service',
#             'objects': http.request.env['uni_health_service.uni_health_service'].search([]),
#         })

#     @http.route('/uni_health_service/uni_health_service/objects/<model("uni_health_service.uni_health_service"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('uni_health_service.object', {
#             'object': obj
#         })