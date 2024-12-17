from odoo import api, fields, models, _
from odoo.exceptions import Warning , ValidationError
from odoo.addons.uni_core.utils import get_default_faculty
from datetime import datetime, timedelta


class AdmissionRecord(models.Model):
    _name = "uni.admission.record"
    _inherit = ['mail.thread']
    _description = "Admission Record"


    name = fields.Char('Name', required=True)

    code = fields.Char("Code", required=True, readonly=True, default=lambda self: _('New'))

    start_date = fields.Date('Start Date', required=True)

    end_date = fields.Date('End Date', required=True)

    academic_year_id = fields.Many2one('uni.year', string="Academic Year", required=True)


    batch_ids =fields.One2many(
        comodel_name="uni.faculty.department.batch",
        inverse_name="admission_record_id")

    state = fields.Selection([
        ('draft', "Draft"),
        ('approved', "Approved"),
        ('closed', "Closed"),
    ],
        default='draft'
    )
    
    admission_program_plan_ids = fields.One2many(
        comodel_name = 'uni.admission.program.plan',
        inverse_name ='admission_record_id'
        )

    admission_ids = fields.One2many(
        'uni.admission',
        inverse_name='admission_record_id'
        )

    @api.constrains('name','code','academic_year_id')
    def _check_name(self):
        for record in self:
            admission_record_id = self.env['uni.admission.record'].search(['|',('name','=ilike',record.name),('code','=ilike',record.code),('id','!=',record.id)])
            admission_record_year_id = self.env['uni.admission.record'].search([('academic_year_id','=',record.academic_year_id.id),('id','!=',record.id)])           
            if admission_record_id:
                raise ValidationError(_("There is another admission record with the same name or code: %s" % admission_record_id.name))
            if admission_record_year_id:
                raise ValidationError(_("It is not possible to create more than one admission record for the same academic year"))


    def action_approve(self):
        batch_id = self.env['uni.faculty.department.batch'].search([('admission_record_id','=',self.id),('state','!=','under_study')])
        if batch_id:
            raise ValidationError(_("There is a batch that has not yet been approved!"))

        self.state = 'approved'

    def action_close(self):
        self.state = 'closed'

    def rest_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, values):
        if values.get('code', _('New')) == _('New'):
            academic_year_id = self.env['uni.year'].browse(values['academic_year_id'])
            code_sequence = self.env['ir.sequence'].next_by_code('admission.record.sequence') or _('New')
            values['code'] = academic_year_id.code + '-' + str(code_sequence)

        res = super(AdmissionRecord, self).create(values)
        return res


    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('The record must be in dratf state to be deleted.'))
            else:
                return super(AdmissionRecord, self).unlink()

        
class AdmissionProgramPlan(models.Model):
    _name = "uni.admission.program.plan"
    _description = "Program Admission Plan"

    program_id = fields.Many2one('uni.faculty.program', string="Program", required=True)

    nationality_type_id = fields.Many2one('uni.nationality.type', string="Nationality")

    transference = fields.Integer('Transference')
    academic_degrees = fields.Integer('Bridging', help="Bridging and holders of academic degrees")
    mature = fields.Integer('Mature')
    add_new = fields.Integer('New')
    academic_degree_holders = fields.Integer('Academic Degree Holder')
    total_student = fields.Integer(compute="compute_total_student", store=True)
    admission_record_id = fields.Many2one('uni.admission.record')

    @api.depends('transference','academic_degrees','mature','add_new','academic_degree_holders')
    def compute_total_student(self):
        for record in self:
            record.total_student = record.transference + record.academic_degrees + record.mature + record.add_new + record.academic_degree_holders
