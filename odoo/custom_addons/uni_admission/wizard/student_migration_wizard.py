# -*- encoding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime


class MigrationWizard(models.TransientModel):
    _name = 'student.migration.wizard'
    _description = 'Student Migration Wizard'

    nationality_type_id = fields.Many2one(
        string="Nationality Type",
        comodel_name="uni.nationality.type",
        ondelete="restrict",
        required=True
    )

    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
        required=True
    )

    def process_migrate(self):
        candidate_student_ids = self.env['student.migration'].browse(self._context.get('active_ids', []))

        for candidate_std in candidate_student_ids:
            batch = max(self.env['uni.faculty.department.batch'].search([('program_id','=',candidate_std.program_id.id)]).ids)
            
            admission_request = self.env['uni.admission'].create({
                'first_name': candidate_std.first_name,
                'middle_name': candidate_std.middle_name,
                'last_name': candidate_std.last_name,
                'fourth_name': candidate_std.fourth_name,
                'university_id': candidate_std.university_id,
                'secondary_school': candidate_std.secondary_school,
                'state': 'candidate',
                'program_id': candidate_std.program_id.id,
                'batch_id': batch,
                'acadimic_year_id': self.year_id.id,
                'nationality_type_id': self.nationality_type_id.id,
                })

            candidate_std_partner = self.env['res.partner'].create({
                'name': admission_request.name,
                'display_name': admission_request.name,
                'active': True,
                'invoice_warn': 'no-message',
                'customer_rank': 1,
                })

            candidate_std_user = self.env['res.users'].create({
                'login': candidate_std.university_id,
                'password': candidate_std.university_id,
                'partner_id': candidate_std_partner.id,
                'notification_type': 'email',
                'odoobot_state': 'onboarding_emoji',
                }) 

            admission_request.write({
                'user_id': candidate_std_user.id,
                })


        candidate_student_ids.unlink()
       