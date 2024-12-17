from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.addons.uni_core.utils import get_default_faculty


class Subject(models.Model):
    _name = 'uni.faculty.subject'
    _description = 'Subject'
    _inherit = ['mail.thread']
    _order = 'active desc , name'
    _rec_name = 'name'


    name = fields.Char(string='Name', required=True)

    english_name = fields.Char(string='English Name', required=True)

    code = fields.Char(string='Code', required=True)

    subject_type = fields.Selection([('theoretical','Theoretical'),
        ('practical','Practical'),
        ('both','Theoretical & Practical'),
        ('tpt','Theoretical & Practical & Tutorial'),
        ('tt','Theoretical & Tutorial')]
        ,string='Type', required=True)

    fail_remove = fields.Boolean('Fail can be removed', default=True)

    practical_lectures = fields.Integer('PR Lectures No.')

    theoretical_lectures = fields.Integer('TH Lectures No.')

    practical_hours = fields.Integer('PR Contact Hours No.')

    practical_credit_hours = fields.Float('PR Credit hours')#, compute="_calc_credit_hours", store=True)

    theoretical_credit_hours = fields.Integer('TH Credit hours')

    tutorial_lectures = fields.Integer('TU Lectures No.')

    tutorial_contact_hours = fields.Integer('TU Contact Hours No.')

    tutorial_credit_hours = fields.Integer('TU Credit hours')

    description = fields.Text('Description', required=True)

    teacher_ids = fields.Many2many('hr.employee',string="Teachers")

    program_ids = fields.Many2one('uni.faculty.program', string="Program", required=True)

    department_id = fields.Many2one(
        'uni.faculty.department',
        string='Department',
    )

    
    
    credit_hours = fields.Integer(
        string='Total Credit Hours',
        #compute='_compute_credit_hours',
        #store=True
    )

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        string='Faculty',
        default=lambda self: get_default_faculty(self),
        required=True
    )

    subject_line_ids = fields.One2many(
        string="Subject Details",
        inverse_name="subject_id",
        comodel_name="uni.faculty.subject.line",
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id
    )

    active = fields.Boolean(default=True)

    migration_code = fields.Char('Migration Code')

    level_id = fields.Many2one(
        string="Level",
        comodel_name="uni.faculty.level",
    )

    semester_id = fields.Many2one(
        string="Term",
        comodel_name="uni.faculty.semester",
    )

    term_semester_id = fields.Char(string='Semester')
    
    specialization_id = fields.Many2one(
        'uni.faculty.department.specialization',
        string='Specialization',
    )


    # @api.constrains('name')
    # def _check_name(self):
    #     for record in self:
    #         subject_id = self.search([('code','=ilike',record.code),('id','!=',record.id)])
    #         if subject_id:
    #             raise ValidationError(_("There is another subject with the same code: %s" % subject_id.name))
   
    # @api.onchange('practical_hours')
    # def _calc_credit_hours(self):
    #     practical_hours = self.company_id.practical_hours
    #     #for rec in self:
    #     if practical_hours > 0:
    #         practical_hours = practical_hours
    #     else:
    #         practical_hours = 2
    #     self.practical_credit_hours = self.practical_hours/practical_hours

    @api.onchange('subject_type','practical_credit_hours', 'theoretical_credit_hours', 'tutorial_credit_hours')
    def onchange_subject(self):
        total_credit = 0
        #for record in self:
        if self.subject_type == 'both':
            total_credit= self.practical_credit_hours + self.theoretical_credit_hours
        elif self.subject_type == 'theoretical':
            total_credit= self.theoretical_credit_hours
        elif self.subject_type == 'tpt':
            total_credit= self.practical_credit_hours + self.theoretical_credit_hours + self.tutorial_credit_hours
        elif self.subject_type == 'tt':
            total_credit= self.theoretical_credit_hours + self.tutorial_credit_hours
        else:
            total_credit= self.practical_credit_hours
        self.credit_hours = total_credit
        
    # @api.model
    # def create(self, vals):
    #     if vals.get('code', _('New')) == _('New'):
    #         vals['code'] = self.env['ir.sequence'].next_by_code('subject.sequence') or _('New')
    #     result = super(Subject, self).create(vals)
    #     return result


class SubjectLine(models.Model):
    _name = 'uni.faculty.subject.line'
    _description = 'Subject Details'
    _rec_name = 'subject_id'

    # To use later in domains
    faculty_id = fields.Many2one(
        comodel_name='res.company',
        related='subject_id.faculty_id',
        string='Faculty',
    )

    level_id = fields.Many2one(
        string="Year",
        comodel_name="uni.faculty.level",
        domain="[('faculty_id', '=', faculty_id)]",
        required=True
    )

    semester_id = fields.Many2one(
        string="Term",
        comodel_name="uni.faculty.semester",
        domain="[('faculty_id', '=', faculty_id)]",
        required=True
    )
    
    department_id = fields.Many2one(
        'uni.faculty.department',
        string='Department',
        required=True,
        domain="[ ('faculty_id', '=', faculty_id)]"
    )

    specialization_id = fields.Many2one(
        string="Specialization",
        comodel_name="uni.faculty.department.specialization",
        domain="[('department_id.faculty_id', '=', faculty_id)]",
    )

    subject_id = fields.Many2one(
        string="Subject",
        comodel_name="uni.faculty.subject",
    )

    credit_hours = fields.Float(string='Credit hours')

    # _sql_constraints = [
    #     (
    #         'subject_details_unique',
    #         'UNIQUE(faculty_id, level_id, semester_id, specialization_id, subject_id)',
    #         _('The subject details must be unique')
    #     ),
    # ]

    @api.constrains('credit_hours')
    def _check_credit_hours(self):
        for r in self:
            if r.credit_hours <= 0:
                raise ValidationError(
                    _('Credit hours must be greater than zero')
                )

    
