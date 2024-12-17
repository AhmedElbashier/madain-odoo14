from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class DiscountScholarshipRequest(models.Model):
    _name = 'uni.discount_scholarship.request'
    _inherit = ['mail.thread']
    _rec_name ='sequence'

    active = fields.Boolean(default=True)

    type = fields.Selection([
        ('student','Student'),
        ('candidate','Candidate')
    ])
    
    state = fields.Selection([
        ('draft','Draft'),
        ('waiting_for_approval','Waiting for Approval'),
        ('approved','Approved'),
        ('rejected','Rejected'),
        ('closed','Closed')
    ], string='Status',readonly=True, default='draft',track_visibility= "always")

    sequence =fields.Char(string='Sequence', required=True, copy=False, readonly=True, default='New')
    
    academic_year_id =fields.Many2one(
        'uni.year',
        string="Academic Year",
        required=True
    )

    admission_year_id =fields.Many2one(
        'uni.year',
        string="Admission Year",
        required=True
    )

    type_of_dis = fields.Selection([
        ('discount','Discount'),
        ('scholarship','Scholarship')
    ], string="Type", required=True)
    
    discount_scholarship_id = fields.Many2one(
        'uni.discount.scholarship',
        string="Type",
        required=True
    )
    
    student_id =fields.Many2one(
        'uni.student',
        string="Student",
        domain="[('state','=','student')]",
    )

    student_program_id = fields.Many2one('uni.faculty.program', related='student_id.program_id')

    candidate_id = fields.Many2one(
        'uni.admission',
        string="Candidate",
        domain=[('state','not in',('registered','rejected'))],
    )

    # if scholarship
    program_id = fields.Many2many(
        'uni.faculty.program',
        string="Programs"
    )
    
    certificate_info =fields.Char(string="Certificate Info")

    # if discount
    sibling_status = fields.Selection([
        ('student','Student'),
        ('candidate','Candidate')
    ])
    sibling_candidate_id = fields.Many2one(
        'uni.admission',
        string="Candidate",
        domain=[('state','not in',('registered','rejected'))],
    )
    sibling_student_id =fields.Many2one('uni.student', string="Sibling")
    siblings = fields.Boolean(related='discount_scholarship_id.siblings')
    candidate = fields.Boolean()
    discount_to = fields.Selection([
        ('two_brother','Two Brother'),
        ('only_one','Only One')
    ])
    
    percentage = fields.Float(string="Precentage")

    second_sibling = fields.Boolean()

    first_brother_percentage = fields.Float(string="First Sibling Discount")

    second_brother_percentage = fields.Float(string="Second Sibling Discount")

    fees_amount = fields.Float(required=True)

    discounted_amount = fields.Float(compute="compute_discount_amounts")

    total_amount = fields.Float(compute="compute_discount_amounts")

    reason = fields.Char()
    
    guardian_name =fields.Many2one('uni.student.guradian')
    
    #phone = fields.Char(related='guardian_name.phone')

    start_date = fields.Date('Start Date')

    end_date = fields.Date('End Date')

    @api.onchange('discount_scholarship_id','student_id','sibling_student_id','sibling_candidate_id','sibling_status')
    def _onchange_discount_scholarship_id(self):
        if self.discount_scholarship_id.type_id == 'discount':
            self.siblings = self.discount_scholarship_id.siblings
            if self.siblings:
                self.discount_to = self.discount_scholarship_id.discount_to
                self.first_brother_percentage = self.discount_scholarship_id.first_brother_percentage
                self.second_brother_percentage = self.discount_scholarship_id.second_brother_percentage
                if self.discount_to == 'two_brother':
                    max_percentage = max(self.discount_scholarship_id.second_brother_percentage,self.discount_scholarship_id.first_brother_percentage)
                    min_percentage = min(self.discount_scholarship_id.second_brother_percentage,self.discount_scholarship_id.first_brother_percentage)
                    if self.type == 'student':
                        if self.sibling_status == 'student' and self.sibling_student_id:
                            if self.student_id.first_registration and self.sibling_student_id.first_registration:
                                if self.student_id.first_registration.year != self.sibling_student_id.first_registration.year:
                                    if self.student_id.first_registration > self.sibling_student_id.first_registration:
                                        self.second_sibling = True
                                    else:
                                        self.second_sibling = False
                                        # self.first_brother_percentage = self.discount_scholarship_id.second_brother_percentage
                                        # self.second_brother_percentage = self.discount_scholarship_id.first_brother_percentage
                                else:
                                    if self.student_id.tuition_fees > self.sibling_student_id.tuition_fees:
                                        if self.first_brother_percentage != min_percentage:
                                            self.second_sibling = True
                                        else:
                                            self.second_sibling = False
                                        #self.second_brother_percentage = max_percentage
                                    else:
                                        if self.first_brother_percentage != max_percentage:
                                            self.second_sibling = True
                                        else:
                                            self.second_sibling = False
                                        #self.second_brother_percentage = min_percentage
                    else:
                        if self.sibling_status == 'student': 
                            if self.sibling_student_id:
                                self.second_sibling = True
                            else:
                                self.second_sibling = False
                        else:
                            candidate_tuition_fees,candidate_registration_fees = self.candidate_id.calculate_student_fees()
                            sibling_tuition_fees,sibling_registration_fees = self.sibling_candidate_id.calculate_student_fees()

                            if candidate_tuition_fees > sibling_tuition_fees:
                                if self.first_brother_percentage != min_percentage:
                                    self.second_sibling = True
                                else:
                                    self.second_sibling = False
                                #self.second_brother_percentage = max_percentage
                            else:
                                if self.first_brother_percentage != max_percentage:
                                    second_sibling = True
                                else:
                                    self.second_sibling = False
                                #self.second_brother_percentage = min_percentage


                    # if self.second_sibling:
                    #     first_percentage = self.first_brother_percentage
                    #     scecond_percentage = self.second_brother_percentage
                    #     self.first_brother_percentage = scecond_percentage
                    #     self.second_brother_percentage = first_percentage
       
            else:
                self.percentage = self.discount_scholarship_id.percentage
        if self.discount_scholarship_id.type_id == 'scholarship':
            self.percentage = self.discount_scholarship_id.percentage


    @api.onchange('student_id','candidate_id')
    def _onchange_student(self):
        domain = {}
        if self.type == 'student':
            self.academic_year_id = self.student_id.year_id.id
            self.admission_year_id = self.student_id.admission_year.id
            self.fees_amount = self.student_id.tuition_fees
        else:
            self.academic_year_id = self.candidate_id.acadimic_year_id.id
            self.admission_year_id = self.candidate_id.admission_year.id
            tuition_fees,registration_fees = self.candidate_id.calculate_student_fees()
            self.fees_amount = tuition_fees

        if self.student_id:
            domain = {
                    'domain':{
                        'guardian_name':[('student_id','=',self.student_id.id)],
                    }
                }
        else:
            domain = {
                'domain':{
                    'guardian_name':[('admission_id','=',self.candidate_id.id)],
                }
                }
        return domain

    @api.onchange('academic_year_id')
    def _onchange_academic_year(self):
        self.start_date = self.academic_year_id.start_date
        self.end_date = self.academic_year_id.end_date

        
    @api.onchange('type_of_dis')
    def _onchange_type(self):
        domain = {}
        self.discount_scholarship_id = False
        if self.type_of_dis == 'discount':
            domain = {
                'domain':{
                    'discount_scholarship_id':[('type_id','=','discount'),('state','=','approved')],
                }
            }
        else:
            domain = {
                'domain':{
                    'discount_scholarship_id':[('type_id','=','scholarship'),('state','=','approved')],
                }
                }
        return domain

    def compute_discount_amounts(self):
        percentage = 0.0
        for rec in self:
            if rec.type_of_dis == 'discount':
                if rec.siblings:
                    if rec.second_sibling:
                        percentage = rec.second_brother_percentage
                    else:
                        percentage = rec.first_brother_percentage
                else:
                    percentage = rec.percentage
            else:
                percentage = rec.percentage


            rec.discounted_amount = (rec.fees_amount*percentage/100)
            rec.total_amount = (rec.fees_amount - rec.discounted_amount)

    def action_waiting_for_approval(self):
        self.state='waiting_for_approval'

    def action_approved(self):
        request_id = self.env['uni.discount_scholarship.request']
        if self.siblings:
            if self.discount_to == 'two_brother':
                #if self.type == 'student':
                if self.sibling_status == 'student':
                    request_id = self.copy(default={
                        'type':'student',
                        'student_id':self.sibling_student_id.id,
                        'academic_year_id':self.sibling_student_id.year_id.id,
                        'sibling_status':'student' if self.type == 'student' else 'candidate',
                        'sibling_student_id':self.student_id.id if self.type == 'student' else False,
                        'sibling_candidate_id':self.candidate_id.id if self.type == 'candidate' else False,
                        'second_sibling':True if self.second_sibling == False else False,
                        'fees_amount':self.sibling_student_id.tuition_fees,})
                else:
                    tuition_fees,registration_fees = self.sibling_candidate_id.calculate_student_fees()
                    request_id = self.copy(default={
                        'type':'candidate',
                        'candidate_id':self.sibling_candidate_id.id,
                        'academic_year_id':self.sibling_candidate_id.acadimic_year_id.id,
                        'sibling_status':'student' if self.type == 'student' else 'candidate',
                        'sibling_student_id':self.student_id.id if self.type == 'student' else False,
                        'sibling_candidate_id':self.candidate_id.id if self.type == 'candidate' else False,
                        'second_sibling':True if self.second_sibling == False else False,
                        'fees_amount':tuition_fees,
                       })
                request_id.state='approved'

        ''' Registration Request '''
        request_ids = self.env['uni.registration.request'].search(['|',('student_id','=',self.student_id.id),('student_id','=',self.sibling_student_id.id),('academic_year_id','=',self.academic_year_id.id)])
        if request_ids:
            for request in request_ids:
                percentage = 0.0
                request_line_id = self.env['uni.fees.installment'].search([('registration_request_id','=',request.id)])
                #if not request_line_id:
                if self.type_of_dis == 'scholarship' or not self.siblings:
                    percentage = self.percentage
                else:
                    if request.student_id.id == self.sibling_student_id.id:
                        percentage = self.second_brother_percentage
                    else:
                        percentage = self.first_brother_percentage

                request.discounted_amount = (request.tuition_fees*percentage/100)
                request.discount_record = self.id
                request.total_amount = request.tuition_fees-request.discounted_amount
                request.discount_perc = percentage
                if self.academic_year_id.allow_installment:
                    if self.academic_year_id.discount_payment == 'equally':
                        for line in request_line_id:
                            line.discount_amount = request.discounted_amount/2
                            if line.state == 'approved':
                                line.create_payment(line.discount_amount)
                    else:
                        request_line_id = self.env['uni.fees.installment'].search([('registration_request_id','=',request.id),('first_installment','!=',True)],limit=1)
                        if request_line_id:
                            request_line_id.discount_amount = request.discounted_amount
                            if request_line_id.state == 'approved':
                                request_line_id.create_payment(request_line_id.discount_amount )
                else:
                    request_line_id = self.env['uni.fees.installment'].search([('registration_request_id','=',request.id)],limit=1)
                    if request_line_id:
                        request_line_id.discount_amount = request.discounted_amount
                        if request_line_id.state == 'approved':
                            request_line_id.create_payment(request_line_id.discount_amount )

        self.state='approved'

    def action_rejected(self):
        self.state='rejected'

    def action_set_to_draft(self):
        if self.siblings:
            discount_scholarship_id = self.env['uni.discount_scholarship.request']
            if self.sibling_status == 'student':
               discount_scholarship_id = self.env['uni.discount_scholarship.request'].search([('student_id','=',self.sibling_student_id.id),('state','=','approved'),('siblings','=',True)],limit=1)
            else:
               discount_scholarship_id = self.env['uni.discount_scholarship.request'].search([('candidate_id','=',self.sibling_candidate_id.id),('state','=','approved'),('siblings','=',True)],limit=1)                
            
            discount_scholarship_id.write({'state':'draft'})
            discount_scholarship_id.unlink()

        self.state='draft'
    

    @api.model
    def create(self, vals):
        if vals['type'] == 'student':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('discount.scholarship.request') or ('New') 
        else:
            vals['sequence'] = self.env['ir.sequence'].next_by_code('discount.scholarship.request.candidate') or ('New')
        result = super(DiscountScholarshipRequest, self).create(vals)
        return result

   
    def attachment_tree_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        action['domain'] = str([
            ('res_model', '=', 'uni.discount_scholarship.request'),
            ('res_id', 'in', self.ids)
            
        ])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        return action

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('The record must be in draft state to be deleted.'))
            else:
                return super(DiscountScholarshipRequest, self).unlink()

