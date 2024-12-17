from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class Batch(models.Model):
    _name = 'uni.faculty.department.batch'
    _inherit = ['mail.thread']
    _description = 'Batch'
    _rec_name = 'code'

    def get_default_level(self):
        level_id = self.env['uni.faculty.level'].search([('order','=','1')],limit=1).id
        semester_id = self.env['uni.faculty.semester'].search([('order','=','1')],limit=1).id

        return level_id

    def get_default_semester(self):
        semester_id = self.env['uni.faculty.semester'].search([('order','=','1')],limit=1).id

        return semester_id

    name = fields.Char(string="Name", translate=True, required=True)

    code = fields.Char(string="Code")

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        string='Faculty',
        default=lambda self: get_default_faculty(self),
        required=True
    )

    department_id = fields.Many2one(
        'uni.faculty.department',
        string='Department',
        domain="[('faculty_id', '=', faculty_id)]",
        #required=True
    )

    program_id = fields.Many2one(
        'uni.faculty.program',
        domain="[('state','=','approved')]",
        string="Program",
        required=True
        )
   
    curriculum_id = fields.Many2one(
        string="Curriculum",
        comodel_name="uni.faculty.curriculum",
        domain="[('program_id', '=', program_id),('template_curriculum','=',True)]",
        ondelete="restrict",
    )

    level_id = fields.Many2one(
        string="Current Level",
        comodel_name="uni.faculty.level",
        required=True,
        default=get_default_level,
    )

    semester_id = fields.Many2one(
        string="Current Term",
        comodel_name="uni.faculty.semester",
        required=True,
        default=get_default_semester,
    )


    state = fields.Selection([
        ('new', "New"),
        ('under_study', "Under Study"),
        ('graduated', "Graduated"),
    ],
        default='new'
    )

    @api.constrains('name','program_id')
    def _check_name(self):
        for record in self:
            obj = self.env['uni.faculty.department.batch'].search([
                ('name','=ilike',record.name),
                ('program_id.id','=',record.program_id.id),
                ('id','!=',record.id)
                ])
            if obj:
                raise ValidationError(_("There is another batch with the same name: %s" % record.name))
            
    @api.onchange('program_id')
    def onchange_program_id(self):
        self.curriculum_id = self.program_id.curriculum_id.id

    def action_study(self):
        if not self.curriculum_id:
            raise ValidationError(
                _("Please Configure The Program Default Curriculum")
                )
        curriculum_id = self.curriculum_id.copy(
            default={'template_curriculum':False,'batch_id':self.id,'name':self.code + ' Curriculum'}
        )
   
        self.curriculum_id = curriculum_id.id
        self.state = 'under_study'

    def action_graduate(self):
        self.state = 'graduated'

    def rest_draft(self):
        self.state = 'new'
