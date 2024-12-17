from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.addons.uni_core.utils import get_default_faculty


class Curriculum(models.Model):
    _name = 'uni.faculty.curriculum'
    _inherit = ['mail.thread']
    _description = 'Curriculum'

    name = fields.Char(string='Name', required=True, translate=True)

    code = fields.Char("Code", required=True, copy=False, readonly=True, default=lambda self: _('New'))

    template_curriculum = fields.Boolean(default=True)

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        string='Faculty',
        # domain="[('type', '=', 'faculty')]",
        default=lambda self: get_default_faculty(self),
        required=True
    )

    department_id = fields.Many2one(
        'uni.faculty.department',
        string='Department',
    )

    program_id = fields.Many2one(
        'uni.faculty.program',
        string='Program',
        required=True
    )

    curriculum_line_ids = fields.One2many(
        string="Curriculum Details",
        inverse_name="curriculum_id",
        comodel_name="uni.faculty.curriculum.line",
        copy=True
    )

    curriculum_subjets_line_ids = fields.One2many(
        string="Curriculum Subjects",
        inverse_name="curriculum_id",
        comodel_name="curriculum.subjects.line",
        copy=True
    )
    
    batch_id = fields.Many2one(
        'uni.faculty.department.batch',
        string='Batch',
    )

    active = fields.Boolean(default=True)

    state = fields.Selection([
        ('draft', "Draft"),
        ('approved', "Approved"),
        ('closed', "Closed"),
    ],
        default='draft'
    )

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            curriculum_id = self.search(['|',('name','=ilike',record.name),('code','=ilike',record.code),('id','!=',record.id)],limit=1)
            if curriculum_id:
                raise ValidationError(_("There is another curriculum with the same name or code: %s" % curriculum_id.name))
    
    def action_approve(self):
        self.curriculum_line_ids.unlink()
        for line in self.curriculum_subjets_line_ids:
            for subject in line.subject_ids:
                curriculum_line_id = self.curriculum_line_ids.create({
                    'level_id':line.level_id.id,
                    'semester_id':line.semester_id.id,
                    'term_semester_id':line.term_semester_id,
                    'subject_id':subject.id,
                    'curriculum_id':self.id,
                    'subject_type':subject.subject_type
                    })
                if subject.subject_type == 'theoretical' or subject.subject_type == 'both':
                    curriculum_line_id.theoretical_lectures = subject.theoretical_lectures
                    curriculum_line_id.theoretical_credit_hours = subject.theoretical_credit_hours
                if subject.subject_type == 'practical' or subject.subject_type == 'both':
                    curriculum_line_id.practical_lectures = subject.practical_lectures
                    curriculum_line_id.practical_hours = subject.practical_hours
                    curriculum_line_id.practical_credit_hours = subject.practical_credit_hours
        self.state = 'approved'

    def action_close(self):
        self.state = 'closed'

    def rest_draft(self):
        self.state = 'draft'
        
    @api.model
    def create(self, values):
        if values.get('code', _('New')) == _('New'):
            program_id = self.env['uni.faculty.program'].browse(values['program_id'])
            code_sequence = self.env['ir.sequence'].next_by_code('curriculum.sequence') or _('New')
            values['code'] = program_id.code+ '-' + str(code_sequence)
        res = super(Curriculum, self).create(values)
        return res

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('The record must be in dratf state to be deleted.'))
            else:
                return super(Curriculum, self).unlink()


class CurriculumLine(models.Model):
    _name = 'uni.faculty.curriculum.line'
    _description = 'Curriculum Details'
    _rec_name = 'curriculum_id'
    _order = 'level_id asc , semester_id asc'

    curriculum_id = fields.Many2one(
        string="Curriculum",
        comodel_name='uni.faculty.curriculum',
    )

    # To use later in domains
    faculty_id = fields.Many2one(
        comodel_name='res.company',
        related='curriculum_id.faculty_id',
        string='Faculty',
    )

    level_id = fields.Many2one(
        string="Level",
        comodel_name="uni.faculty.level",
        required=True
    )

    semester_id = fields.Many2one(
        string="Term",
        comodel_name="uni.faculty.semester",
        required=True
    )

    term_semester_id = fields.Char('Semester')

    department_id = fields.Many2one(
        'uni.faculty.department',
        string='Department',
    )

    subject_id = fields.Many2one(
        string="Subject",
        comodel_name="uni.faculty.subject",
        required=True
    )

    teacher_ids = fields.Many2many('hr.employee',related='subject_id.teacher_ids',string="Teachers")

    teacher_id = fields.Many2one('hr.employee',domain="[('id','in',teacher_ids)]")

    specialization_id = fields.Many2one(
        'uni.faculty.department.specialization',
        domain=[('state','=','approved')],
        string='Specialization',
        ondelete="restrict",
        )

    subject_type = fields.Selection([('theoretical','Theoretical'),
        ('practical','Practical'),
        ('both','Theoretical & Practical'),
        ('tpt','Theoretical & Practical & Tutorial'),
        ('tt','Theoretical & Tutorial'),
        ]
        ,string='Type')

    practical_hours = fields.Integer('Number Of Hours')

    practical_credit_hours = fields.Float(string='Credit hours', compute="_calc_credit_hours")
    
    practical_lectures = fields.Integer('Lectures No')

    theoretical_lectures = fields.Integer('Lectures No')

    theoretical_credit_hours = fields.Float(string='Credit hours')

    credit_hours = fields.Integer(
        string='Credit Hours',
        compute='_compute_credit_hours',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id
    )

    @api.onchange('subject_id')
    def onchange_subject_id(self):
        self.subject_type = self.subject_id.subject_type
        if self.subject_id.subject_type == 'theoretical' or self.subject_id.subject_type == 'both':
            self.theoretical_lectures = self.subject_id.theoretical_lectures
            self.theoretical_credit_hours = self.subject_id.theoretical_credit_hours
        if self.subject_id.subject_type == 'practical' or self.subject_id.subject_type == 'both':
            self.practical_lectures = self.subject_id.practical_lectures
            self.practical_credit_hours = self.subject_id.practical_credit_hours
            self.practical_hours = self.subject_id.practical_hours


    @api.depends('practical_hours')
    def _calc_credit_hours(self):
        practical_hours = self.company_id.practical_hours
        for rec in self:
            if practical_hours > 0:
                practical_hours = practical_hours
            else:
                practical_hours = 2
            rec.practical_credit_hours = rec.practical_hours/practical_hours

    @api.depends('subject_type','practical_credit_hours', 'theoretical_credit_hours')
    def _compute_credit_hours(self):
        total_credit = 0
        for record in self:
            if record.subject_type == 'both':
                total_credit= record.practical_credit_hours + record.theoretical_credit_hours
            elif record.subject_type == 'theoretical':
                total_credit= record.theoretical_credit_hours
            else:
                total_credit= record.practical_credit_hours
            record.credit_hours = total_credit

class CurriculumSubjectsLine(models.Model):
    _name = 'curriculum.subjects.line'
    _description = 'Curriculum Subjects'


    level_id = fields.Many2one(
        string="Level",
        comodel_name="uni.faculty.level",
        required=True
    )

    semester_id = fields.Many2one(
        string="Term",
        comodel_name="uni.faculty.semester",
        required=True
    )

    term_semester_id = fields.Char(compute="compute_semeser",string='Semester', store=True)

    subject_ids = fields.Many2many(
        string="Subject",
        comodel_name="uni.faculty.subject",
        required=True
    )

    curriculum_id = fields.Many2one(
        string="Curriculum",
        comodel_name='uni.faculty.curriculum',
    )

    program_id = fields.Many2one(
        'uni.faculty.program',
        related='curriculum_id.program_id',
        string='Program',
        required=True
    )

    @api.depends('level_id','semester_id')
    def compute_semeser(self):
        for rec in self:
            if rec.semester_id.order == '2':
                rec.term_semester_id = int(rec.level_id.order)*int(rec.semester_id.order)
            elif rec.semester_id.order == '1':
                rec.term_semester_id = (int(rec.level_id.order)*2)-1



