from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime

class Program(models.Model):
    _name = 'uni.faculty.program'
    _inherit = ['mail.thread']
    _description = 'Programs'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)

    english_name = fields.Char(string='Name', required=True)

    code = fields.Char(string='Code', required=True)

    coordinator = fields.Many2one('hr.employee', required=True)

    description = fields.Text('Description', required=True)

    sequence_id = fields.Many2one('ir.sequence')

    curriculum_id = fields.Many2one(
        string="Curriculum",
        comodel_name="uni.faculty.curriculum",
        domain="[('program_id', '=', id)]",
    )

    coordinators_history_ids = fields.One2many(
        string="Coordinators",
        comodel_name="program.coordinator.history",
        inverse_name="program_id"
    )

    state = fields.Selection([
        ('draft', "Draft"),
        ('approved', "Approved"),
        ('closed', "Closed"),
    ],
        default='draft'
    )
   
    @api.constrains('name','code')
    def _check_name(self):
        for record in self:
            program_id = self.env['uni.faculty.program'].search(['|',('name','=ilike',record.name),('code','=ilike',record.code),('id','!=',record.id)],limit=1)

            if program_id:
                raise ValidationError(_("There is another program with the same name or code: %s" % program_id.name))
            
    def action_approve(self):
        if not self.curriculum_id:
            raise ValidationError(_("The Curriculum must be set before approving the program"))

        self.state = 'approved'

    def action_close(self):
        self.state = 'closed'

    def rest_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, values):
        values['sequence_id'] = self.env['ir.sequence'].create({
            'name':values['name'],
            'code':values['name'],
            'padding':3,
            }).id

        # if len(values['code']) != 3:
        #     raise ValidationError(_("Code length must be equal 3"))

        res = super(Program, self).create(values)
        return res


    @api.depends('coordinator')
    @api.onchange('coordinator')
    def onchange_coordinator(self):
        if self.name:
            history_id = self.env['program.coordinator.history'].create({
                'program_id':self.id,
                'coordinator_id' : self.coordinator.id,
                'start_date' : fields.Date.today(),
                })
            
            query = ("""
                    update program_coordinator_history
                    set end_date = %(EndDate)s
                    where id = (select max(program_coordinator_history.id) 
                                from program_coordinator_history, uni_faculty_program
                                where program_coordinator_history.program_id =  uni_faculty_program.id
                                and uni_faculty_program.name = %(ProgName)s)

            """)
            self._cr.execute(query,{'EndDate': fields.Date.today(), 'ProgName': self.name})


    def specialization_tree_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Specialization',
            'view_mode': 'tree,form',
            'res_model': 'uni.faculty.department.specialization',
            'domain': [('program_id', '=', self.id)],
            'context': {'default_program_id': self.id},
            
        }

                    
class ProgramCoordinatorHistory(models.Model):
    _name = 'program.coordinator.history'
    _description = 'Legacy Coordination Data'
    program_id = fields.Many2one('uni.faculty.program')
    coordinator_id = fields.Many2one('hr.employee')
    start_date = fields.Date(string='Strat Date')
    end_date = fields.Date(string='End Date')

    # def unlink(self):
    #     for rec in self:
    #         if self.end_date:
    #             raise ValidationError(_("This Record Contains End Date: %s" % self.end_date))
    #     rtn = super(ProgramCoordinatorHistory,self).unlink
    #     return rtn