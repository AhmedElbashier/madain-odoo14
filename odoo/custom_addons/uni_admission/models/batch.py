# -*- encoding: utf-8 -*-
from odoo import api, fields, models

class Batch(models.Model):
    _inherit = 'uni.faculty.department.batch'



    academic_year_id = fields.Many2one(
        'uni.year',
        string="Academic Year",
        required=True
    )
    
    admission_record_id = fields.Many2one(
            'uni.admission.record',
        )

    admission_year_id = fields.Many2one(
        'uni.year',
        string="Admission Year",
        required=True
    )

    registered_fees_ids = fields.One2many(
        comodel_name="uni.registered.fees",
        inverse_name="batch_id",
    )

    batch_installment_ids = fields.One2many(
        comodel_name='uni.fees.installment',
        inverse_name="uni_faculty_batch",
        )

    next_level_id = fields.Many2one(
        'uni.faculty.level',
        string="Next Level",
    )

    @api.model
    def create(self, values):
        program_id = self.env['uni.faculty.program'].browse(values['program_id'])
        academic_year_id = self.env['uni.year'].browse(values['academic_year_id'])
        code_sequence = program_id.sequence_id.next_by_code(program_id.sequence_id.code) or '/'
        values['code'] = program_id.code + '-' + academic_year_id.code + '-' + str(code_sequence)

        res = super(Batch, self).create(values)
        return res
