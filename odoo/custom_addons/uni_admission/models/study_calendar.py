from odoo import api, fields, models
from odoo.tools.translate import _


class FacultyCalendar(models.Model):
    _inherit = 'uni.faculty.calendar'

    academic_year_id = fields.Many2one(
        'uni.year',
        string="Academic Year",
    )

    # @api.model
    # def create(self, values):
    #     academic_year_id = self.env['uni.year'].browse(values['academic_year_id'])
    #     values['code'] = academic_year_id.code + '-' + self.env['ir.sequence'].next_by_code('uni.faculty.calendar') or '/'
    #     return super(FacultyCalendar, self).create(values)