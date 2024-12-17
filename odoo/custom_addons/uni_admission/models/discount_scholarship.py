from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DiscountScholarship(models.Model):
    _name = 'uni.discount.scholarship'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)

    code = fields.Char(required=True)

    type_id = fields.Selection([
        ('discount','Discount'),
        ('scholarship','Scholarship')
    ],default='discount' , string="Type")
    
    discount_scholarship_type=fields.Selection([
        ('yearly','Yearly'),
        ('permanent','Permanent'),
        ('permanent&being_reviewed','Permanent & Being reviewed')
    ],string="Type" )
    
    siblings = fields.Boolean()

    repeat = fields.Boolean('Repeat Discount')
    
    discount_to = fields.Selection([
        ('two_brother','Two Brother'),
        ('only_one','Only One')
    ],default='only_one', string="Discount to")
    
    percentage = fields.Float(string="Precentage")

    first_brother_percentage = fields.Float(string="First Sibling(%)")

    second_brother_percentage = fields.Float(string="Second Sibling(%)")

    discount_account_id = fields.Many2one(
        'account.account',
        string="Account"
    )
    
    scholarship_account_id = fields.Many2one(
        'account.account',
        string="Account"
    )

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
            discount_id = self.search(['|',('name','=ilike',record.name),('code','=ilike',record.code),('id','!=',record.id)],limit=1)
            if discount_id:
                raise ValidationError(_("There is another discount or scholarship with the same name or code: %s" % discount_id.name))
    
    def action_approve(self):
        self.state = 'approved'
        
    def action_close(self):
        self.state = 'closed'

    def rest_draft(self):
        self.state = 'draft'

class Year(models.Model):
    _inherit = 'uni.year'
        

    discount_payment = fields.Selection([('equally','Equally'),('2nd_nstallment','2nd Installment')],default='equally',string='Scholarships&Discounts Payment', required=True)
