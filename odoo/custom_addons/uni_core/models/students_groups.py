

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Groups(models.Model):
    _name = 'uni.student.groups'
    _inherit = ['mail.thread']


    name = fields.Char(string='Name', required=True)

    code = fields.Char(string='Code')
    
    program_id = fields.Many2one(
        'uni.faculty.program',
        string='Program',
        required=True
    )

    level_id = fields.Many2one(
        string="Level",
        comodel_name="uni.faculty.level",
        required=True,
    )

    semester_id = fields.Many2one(
        string="Term",
        comodel_name="uni.faculty.semester",
        required=True,
    )

    batch_id = fields.Many2one(
        'uni.faculty.department.batch',
        string='Batch',
        required=True,
    )

    student_ids = fields.Many2many(
        string="Students",
        comodel_name="uni.student",
        required=True,
    )

    @api.constrains('student_ids')
    def check_student_ids(self):
        for rec in self:
            group_id = self.env['uni.student.groups'].search([('student_ids','in',rec.student_ids.ids),('id','!=',rec.id),('academic_year_id','=',self.academic_year_id.id)],limit=1)
            if group_id:
                raise ValidationError(_("Thee student must not appear in more than one group"))


    # @api.model
    # def create(self, vals):
    #     vals['code'] = self.env['ir.sequence'].next_by_code(
    #     'students.groups') or '/'
    #     return super(Groups, self).create(vals)

