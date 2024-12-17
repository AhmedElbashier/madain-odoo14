# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _

class ConfirmationWizard(models.TransientModel):
    _name = 'confirm.wizard'
    _description = 'Confirmation Wizard'

    student_services_id = fields.Many2one('uni.faculty.student.services')

    suspension_id = fields.Many2one('uni.faculty.student.services')

    general_service_id = fields.Many2one('uni.general.services')

    admission_service_id = fields.Many2one('admission.services')

    late_registration_id = fields.Many2one('uni.late.registration')

    permission_service_id = fields.Many2one('uni.student.permissions')

    substitution_service_id = fields.Many2one('substitution.service')

    fail_removal_service_id = fields.Many2one('fail.removal')

    recorrection_service_id = fields.Many2one('uni.student.recorrection')

    def action_continue(self):
        if self.env.context.get('student_services_id'):
            student_services_id = self.env['uni.faculty.student.services'].browse(self._context.get('active_ids', []))
            student_services_id.action_confirm()

        # admission_services_id = self.env['admission.services'].browse(self._context.get('active_ids', []))
        # if admission_services_id:
        #     admission_services_id.action_draft()

        if self.env.context.get('general_service_id'):
            general_services_id = self.env['uni.general.services'].browse(self._context.get('active_ids', []))
            general_services_id.action_confirm()

        if self.env.context.get('fail_removal_service_id'):
            fail_removal_services_id = self.env['fail.removal'].browse(self._context.get('active_ids', []))
            fail_removal_services_id.action_confirm()

        if self.env.context.get('late_registration_id'):
            late_registration_services_id = self.env['uni.late.registration'].browse(self._context.get('active_ids', []))
            late_registration_services_id.action_confirm()

        if self.env.context.get('permission_service_id'):
            permission_services_id = self.env['uni.student.permissions'].browse(self._context.get('active_ids', []))
            permission_services_id.action_confirm()

        if self.env.context.get('recorrection_service_id'):
            recorrection_services_id = self.env['uni.student.recorrection'].browse(self._context.get('active_ids', []))
            recorrection_services_id.to_examination_committee()
        
        if self.env.context.get('substitution_service_id'):
            substitution_services_id = self.env['substitution.service'].browse(self._context.get('active_ids', []))
            substitution_services_id.action_confirm()
