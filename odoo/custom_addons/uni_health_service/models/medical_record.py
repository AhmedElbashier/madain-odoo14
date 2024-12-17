from datetime import datetime
from odoo import api, fields, models


class MedicalRecord(models.Model):
    _name = 'uni.health_service.medical_record'
    _description = 'Medical Record'
    _rec_name = 'student_id'

    student_id = fields.Many2one(
        comodel_name='uni.student', string='Student', required=True)

    faculty_id = fields.Many2one(
        'res.company', related='student_id.faculty_id', readonly=True
    )

    date = fields.Datetime(
        string='Date', required=True, default=datetime.now())

    doctor_id = fields.Many2one(
        comodel_name='res.users', string='Doctor', required=True)

    pharmacist_id = fields.Many2one(
        comodel_name='res.users', string='Pharmacist')

    treatment = fields.Text(string='Treatment', required=True)
