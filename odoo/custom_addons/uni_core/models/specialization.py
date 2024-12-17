from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

class Specialization(models.Model):
    _name = 'uni.faculty.department.specialization'
    _inherit = ['mail.thread']
    _description = 'Specialization'

    name = fields.Char(string='Name', required=True, translate=True)

    english_name = fields.Char(string='English Name', required=True)

    code = fields.Char('Code', required=True)

    state = fields.Selection([
        ('draft', "Draft"),
        ('approved', "Approved"),
        ('closed', "Closed"),
    ],
        default='draft'
    )

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        string='Faculty',
        # domain="[('type', '=', 'faculty')]",
        default=lambda self: get_default_faculty(self),
        required=True
    )

    program_id = fields.Many2one(
        'uni.faculty.program',
        domain=[('state','!=','closed')],
        string="Program",
        required=True)

    department_id = fields.Many2one(
        'uni.faculty.department',
        string='Department',
        domain="[ ('faculty_id', '=', faculty_id)]"
    )

    student_ids = fields.One2many('uni.student', 'specialization_id')

    parent_id = fields.Many2one(
        'uni.faculty.department.specialization',
        string='Parent Specialization'
    )

    parent_left = fields.Integer(string='Parent Left', invisible=True)
    
    parent_right = fields.Integer(string='Parent Right', invisible=True)

    @api.constrains('name','code')
    def _check_name(self):
        for record in self:
            specialization_id = self.env['uni.faculty.department.specialization'].search(['|',('name','=ilike',record.name),('code','=ilike',record.code),('id','!=',record.id)])
            if specialization_id:
                raise ValidationError(_("There is another Specialization with the same name or code: %s" % specialization_id.name))

    
    def action_approve(self):
        self.state = 'approved'

    def action_close(self):
        self.state = 'closed'

    def rest_draft(self):
        self.state = 'draft'

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('The record must be in dratf state to be deleted.'))
            else:
                return super(Specialization, self).unlink()
