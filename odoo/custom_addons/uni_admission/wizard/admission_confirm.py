# -*- encoding: utf-8 -*-

from odoo import api, fields, models


class ConfirmationWizard(models.TransientModel):
    _name = 'admission.confirm.wizard'
    _description = 'Admission Confirmation Wizard'

    def confirm(self):
        candidate_student_ids = self.env['uni.admission'].browse(self._context.get('active_ids', []))
        for candidate in candidate_student_ids:
            if candidate.state == 'draft':
                candidate.to_candidate()
            elif candidate.state == 'candidate':
                candidate.to_wait_interview()
            elif candidate.state == 'wait_interview':
                candidate.to_interview()
            elif candidate.state == 'interview':
                candidate.to_accepted()
            elif candidate.state == 'accepted':
                candidate.create_student_record()