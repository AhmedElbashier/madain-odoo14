from datetime import date, timedelta
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.addons.uni_core.utils import get_default_faculty


class Students(models.Model):
    _name = 'uni.student'
    _description = 'Student'
    #_inherits = {'res.users': 'user_id'}
    _inherit = ['mail.thread']
    _rec_name = 'name'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
        index=True
    )

    name_en = fields.Char(
        string='Name (English)',
        compute='_compute_name_en',
        store=True,
        index=True
    )

    # Arabic
    first_name = fields.Char(string='First name', required=True)
    middle_name = fields.Char(string='Middle name',
                              required=True)
    last_name = fields.Char(string='Last name')
    fourth_name = fields.Char(string='Fourth name')

    # English
    first_name_en = fields.Char(string='First name (English)')
    middle_name_en = fields.Char(string='Middle name (English)')
    last_name_en = fields.Char(string='Last name (English)')
    fourth_name_en = fields.Char(string='Fourth name (English)')

    birth_date = fields.Date(string='Birth date')
    place_of_birth = fields.Char(string='Place of Birth')

    gender = fields.Selection(
        string='Gender',
        selection=[
            ('male', 'Male'),
            ('female', 'Female')
        ]
    )

    nationality_id = fields.Many2one(
        comodel_name='res.country',
        string='Nationality'
    )
    national_id = fields.Char(string="National ID", )

    religion = fields.Selection(string='Religion', selection=[
        ('islam', 'Islam'),
        ('christianity', 'Christianity'),
        ('other', 'Other')
    ])

    university_id = fields.Char(
        string='University ID',
        index=True,
        )

    std_number = fields.Char(
        string='Student Number',
        readonly=True
        )

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: get_default_faculty(self),
        string='Faculty',
        required=True,
        )
    
    program_id = fields.Many2one(
        comodel_name='uni.faculty.program',
        string="Program",
        )
    department_id = fields.Many2one(
        comodel_name='uni.faculty.department',
        domain="[('faculty_id', '=', faculty_id)]",
        string="Department",
        )

    specialization_id = fields.Many2one(
        'uni.faculty.department.specialization',
        string='Specialization',
        )

    batch_id = fields.Many2one(
        'uni.faculty.department.batch',
        string='Batch',
        )

    level_id = fields.Many2one(
        'uni.faculty.level',
        string='Level',
        )

    semester_id = fields.Many2one(
        'uni.faculty.semester',
        string="Term",
        )
    medical_data = fields.Many2one(
        'uni.health_service.medical_data', string="Medical Data")
    address = fields.Char(string="Address")
    secondary_school = fields.Many2one('uni.school',string='Secondary School')
    school_percentage = fields.Char()
   
    user_id = fields.Many2one(
        comodel_name='res.users',
        ondelete="restrict",
        index=True
    )

    state = fields.Selection(
        string="State",
        selection=[
            ('student', 'Student'),
            ('graduate', 'Graduate'),
            ('resigned', 'Resigned'),
            ('dismissed', 'Dismissed'),
            ('frozen', 'Suspended'),
        ],
        default='student',
    )

    guardian_ids = fields.One2many('uni.student.guradian','student_id',string="Guardians")
   
    city = fields.Char(related='user_id.city')

    # image = fields.Char(related='user_id.image')
    std_img = fields.Binary(string="Student Image", )

    contact_ids = fields.One2many('guradian.contact','student_id')
    
    phone = fields.Char(string='Phone(1)')
    
    mobile = fields.Char(string='Phone(2)')
    
    email = fields.Char()

    medical_condition = fields.Selection(
        string="Medical Check",
        selection=[
            ('fit', 'fit'),
            ('unfit', 'unfit'),
        ],
        default="fit",
    )

    committee_head = fields.Char('Head of Committee')
    
    committee_notes = fields.Text(string="Notes", )
    
    committee_recom = fields.Selection(
        string="Committee Recommendation",
        selection=[
            ('accepted', 'Acceptable'),
            ('not_accepted', 'Not Acceptable'),
        ],
        default="accepted",
    )

    martial_status = fields.Selection(
        string="Martial Status",
        selection=[
            ('single', 'Single'),
            ('married', 'Married'),
            ('divorsed', 'Divorsed'),
            ('widow', 'Widow'),
        ],
        default='single',
    )
    
    academic_status = fields.Selection(
        string="Acadimic Status",
        selection=[
            ('fresh', 'Fresh'),
            ('success', 'Success'),
            ('repeat', 'Repeat'),
            ('repeat_subjects','Repeat With Subjects'),
            ('supplement' , 'Has Supplements'),
            ('substitutions', 'Has Substitutionals'),
            ('substitutional_supplement','Has Substitutional & Supplements'),
            ('dismiss','Dismiss'),
        ],
        default='fresh',
    )
    
    partner_id = fields.Many2one('res.partner','Related Partner')
    # attachment_ids = fields.Many2many('ir.attachment', string='Documents', attachment=True, required=True)
    
    @api.constrains("birth_date")
    def _check_birth_date(self):
        # 15 years ago today
        max_date = date.today() - timedelta(days=15*365)
        for r in self:
            if r.birth_date:
                if fields.Date.from_string(r.birth_date) > max_date:
                    raise ValidationError(
                        _("Student age can't be less than 15 years")
                    )

    # @api.constrains("std_number")
    # def _check_std_number(self):
    #     for record in self:
    #         if record.university_id:
    #             student_id = self.search([('std_number','=ilike',record.std_number),('id','!=',record.id)])
    #             if student_id:
    #                 raise ValidationError(_("There is another student with the same number: %s" % student_id.name))
           
    
    _sql_constraints = [
        (
            'university_id_unique', 
            'Check(1=1)',
            _('The university ID must be unique')
        ),
    ]

    @api.depends('first_name', 'middle_name', 'last_name', 'fourth_name')
    def _compute_name(self):
        for record in self:
            record.name = '%s %s %s %s' % (
                record.first_name,
                record.middle_name,
                record.last_name,
                record.fourth_name,
            )

    @api.depends('first_name_en', 'middle_name_en', 'last_name_en', 'fourth_name_en')
    def _compute_name_en(self):
        for record in self:
            record.name_en = '%s %s %s %s' % (
                record.first_name_en,  
                record.middle_name_en,
                record.last_name_en,
                record.fourth_name_en,
            )

    @api.model
    def name_search(self, name, args=[], operator='ilike', limit=100):
        records = self.search(
            ['|', '|', '|', ('university_id', operator, name),
             ('name', operator, name), ('name_en', operator, name), ('std_number', operator, name)] + args,
            limit=limit
        )

        return records.name_get()

    def coll_name(self):
        return self.first_name+" "+self.middle_name+" "+self.last_name+" "+self.fourth_name


    @api.model
    def create(self, values):
        return super(Students, self).create(values)