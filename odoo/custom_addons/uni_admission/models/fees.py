# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError


class TuitionFees(models.Model):
    _name = 'uni.study_fees'
    _description = 'Tuition fees'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)

    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
    )

    nationality_type_id = fields.Many2one(
        comodel_name='uni.nationality.type',
        string='Nationality Type',
    )

    fees_line_ids = fields.One2many(
        comodel_name="uni.study_fees.line",
        inverse_name="fees_id",
    )

    department_line_ids = fields.One2many(
        comodel_name="uni.study_fees.departments",
        inverse_name="fees_id",
    )

    registered_line_ids = fields.One2many(
        comodel_name="uni.registered.fees",
        inverse_name="uni_study_fees_id",
    )

    program_line_ids = fields.One2many(
        comodel_name="uni.program.fees",
        inverse_name="uni_study_fees_id",
    )


    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related='nationality_type_id.currency_id',
        readonly=True,
    )

    state = fields.Selection(
        string="State",
        selection=[
            ('draft', 'Draft'),
            ('approve', 'Waiting for approval'),
            ('done', 'Approved'),
        ],
        default="draft"
    )

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            obj = self.search([('name','=ilike',record.name),('id','!=',record.id)])
            if obj:
                raise ValidationError(_("There is another fees with the same name: %s" % record.name))

            fees_id = self.search([('year_id','=',record.year_id.id),('year_id','!=',False),('id','!=',record.id)],limit=1)
            if fees_id:
                raise ValidationError(_("There is another fees record with a same academic year: %s" % fees_id.name))

    @api.model
    def create(self, values):
        academic_year_id = self.env['uni.year'].search([('id','=',values['year_id'])])
        res = super(TuitionFees, self).create(values)
        academic_year_id.write({
            'fees_id':(4, res.id), 
            })
        return res

    
    @api.onchange('year_id')
    def create_program_fees(self):
        self.program_line_ids.unlink()
        nationality_ids = self.env['uni.nationality.type'].search([])
        for program in self.year_id.program_ids:
            for nationality in nationality_ids:
                program_fees = self.env['uni.program.fees'].create({
                    'program_id':program.id,
                    'nationality_type_id':nationality.id,
                    'uni_study_fees_id':self.id,
                })



    def approve(self):
        if not self.registered_line_ids and not self.program_line_ids:
            raise Warning(
                _('Please add program and/or registration fees!')
            )
        self.write({'state': 'approve'})

    def done(self):
        self.write({'state': 'done'})

    def rest_draft(self):
        self.write({'state': 'draft'})

    def get_year_fees(self):
        for rec in self:
            fees = dict()
            for line in rec.program_line_ids:
                if line.program_id.id in fees:
                    fees[line.program_id.id].append(line.add_new)
                else:
                    fees[line.program_id.id] = [line.program_id.name,line.add_new]
            
        return fees


class TuitionFeesLine(models.Model):
    _name = 'uni.study_fees.line'
    _description = 'Faculty Fees'

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        #domain="[('type', '=', 'faculty')]",
        string='Faculty',
        required=True
    )

    fees_id = fields.Many2one(
        string="Tuition fees",
        comodel_name="uni.study_fees",
    )

    nationality_type_id = fields.Many2one(
        comodel_name='uni.nationality.type',
        string='Nationality Type',
        related='fees_id.nationality_type_id',
    )

    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
        related='fees_id.year_id',
    )

    state = fields.Selection(
        string="State",
        selection=[
            ('draft', 'Draft'),
            ('approve', 'Waiting for approval'),
            ('done', 'Approved'),
        ],
        default="draft",
        related='fees_id.state',
    )

    registration_fees = fields.Float(string="Registration Fees", required=True)
    study_fees = fields.Float(string="Tuition Fees", required=True)


class RegistrationFees(models.Model):
    _name = 'uni.registered.fees'
    _description = 'Registration Fees'

    nationality_type_id = fields.Many2one(
        'uni.nationality.type',
        string='Nationality Type',
        required=True
    )

    registration_fees = fields.Monetary('Fees', required=True, currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', related='nationality_type_id.currency_id')

    uni_study_fees_id = fields.Many2one(
        'uni.study_fees',
        )

    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
        related='uni_study_fees_id.year_id',
    )

    batch_id = fields.Many2one('uni.faculty.department.batch')

    registration_record_id = fields.Many2one('uni.registration.record')

    state = fields.Selection(
        string="State",
        selection=[
            ('draft', 'Draft'),
            ('approve', 'Waiting for approval'),
            ('done', 'Approved'),
        ],
        default="draft",
        related='uni_study_fees_id.state',
    )

    # @api.onchange('nationality_type_id')
    # def onchange_nationality(self):
    #     self.currency_id = self.nationality_type_id.currency_id.id

class ProgramFees(models.Model):
    _name = 'uni.program.fees'
    _description = 'Program Fees'

    program_id = fields.Many2one(
        comodel_name='uni.faculty.program',
        string="Program",
        # required=True,
    )


    nationality_type_id = fields.Many2one(
        'uni.nationality.type',
        string='Nationality Type',
        required=True
    )


    transference = fields.Monetary('Transference', required=True, currency_field='currency_id',default=0.0)
    
    academic_degrees = fields.Monetary('Bridging', help="Bridging and holders of academic degrees",required=True, currency_field='currency_id',default=0.0)
    
    mature = fields.Monetary('Mature', required=True, currency_field='currency_id',default=0.0)

    add_new = fields.Monetary('New Admission', required=True, currency_field='currency_id',default=0.0)

    academic_degree_holders = fields.Monetary('Academic Degree Holder', required=True, currency_field='currency_id',default=0.0)
    
    currency_id = fields.Many2one('res.currency', related='nationality_type_id.currency_id')

    uni_study_fees_id = fields.Many2one(
        'uni.study_fees',
        )

    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
        related='uni_study_fees_id.year_id',
    )

    state = fields.Selection(
        string="State",
        selection=[
            ('draft', 'Draft'),
            ('approve', 'Waiting for approval'),
            ('done', 'Approved'),
        ],
        default="draft",
        related='uni_study_fees_id.state',
    )


    # @api.onchange('nationality_type_id')
    # def onchange_nationality(self):
    #     self.currency_id = self.nationality_type_id.currency_id.id


class TuitionFeesDepartment(models.Model):
    _name = 'uni.study_fees.departments'
    _description = 'Department Fees'

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        #domain="[('type', '=', 'faculty')]",
        string='Faculty',
        required=True,
        default=lambda self: self.env.user.company_id
    )

    department_id = fields.Many2one(
        comodel_name='uni.faculty.department',
        domain="[('faculty_id', '=', faculty_id)]",
        string="Department",
        required=True,
    )

    fees_id = fields.Many2one(
        string="Tuition fees",
        comodel_name="uni.study_fees",
    )

    nationality_type_id = fields.Many2one(
        comodel_name='uni.nationality.type',
        string='Nationality Type',
        related='fees_id.nationality_type_id',
    )
  
    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
        related='fees_id.year_id',
    )

    state = fields.Selection(
        string="State",
        selection=[
            ('draft', 'Draft'),
            ('approve', 'Waiting for approval'),
            ('done', 'Approved'),
        ],
        default="draft",
        related='fees_id.state',
    )

    registration_fees = fields.Float(string="Registration Fees")
    study_fees = fields.Float(string="Tuition Fees", required=True)

class additionalFees(models.Model):
    _name = 'uni.add_fees'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Name',
        required=True
    )

    amount = fields.Float(
        string="Amount",
        required=True,
    )

    account_id = fields.Many2one('account.account')

    @api.depends('name', 'amount ')
    def name_get(self):

        result = []
        for X in self:
            name = ( X.name + '-' or "") + str(X.amount)

            result.append((X.id, name)) 
            
        return result
