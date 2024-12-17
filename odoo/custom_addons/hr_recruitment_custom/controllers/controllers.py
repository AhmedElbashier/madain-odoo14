# -*- coding: utf-8 -*-
# from odoo import http


# class HrRecruitmentCustom(http.Controller):
#     @http.route('/hr_recruitment_custom/hr_recruitment_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_recruitment_custom/hr_recruitment_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_recruitment_custom.listing', {
#             'root': '/hr_recruitment_custom/hr_recruitment_custom',
#             'objects': http.request.env['hr_recruitment_custom.hr_recruitment_custom'].search([]),
#         })

#     @http.route('/hr_recruitment_custom/hr_recruitment_custom/objects/<model("hr_recruitment_custom.hr_recruitment_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_recruitment_custom.object', {
#             'object': obj
#         })
