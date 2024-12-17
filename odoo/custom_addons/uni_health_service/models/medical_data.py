from odoo import models, fields, api


class MedicalData(models.Model):
    _name = 'uni.health_service.medical_data'
    _description = "Medical data"
    _rec_name = "student_id"

    student_id = fields.Many2one('uni.student', string="Student")
    doctor_notes = fields.Text(string='Doctors Notes')
    family_disease_ids = fields.Many2many(
        'uni.health_service.disease','medical_data_family_disease','disease_id','family_disease', string="Family disease's")
    past_disease_ids = fields.Many2many(
        'uni.health_service.disease','medical_data_past_disease','disease_id','past_disease', string="Past History disease's")
    previous_operations = fields.Many2many(
        'surgery', string="Previous operation")
    with_special_needs = fields.Selection(
        string="with special needs",
        selection=[
            ('no', 'No'),
            ('yes', 'Yes'),
        ],
    )

    no_impaired = fields.Boolean(string="None", )
    impaired_hearing = fields.Boolean(string="Impaired hearing", )
    optical_disablity = fields.Boolean(string="Optical disablity", )
    impaired_mobility = fields.Boolean(string="Impaired mobility", )

    type_of_school = fields.Selection(
        string="School Type",
        selection=[
            ('public', 'Public'),
            ('private', 'Private'),

        ],)

    # happits
    cigarettes = fields.Boolean(string="cigarettes", )
    rise_of = fields.Boolean(string="rise Of", )

    injection = fields.Boolean(string="Injection", )
    inhalation = fields.Boolean(string="Inhalation", )
    pills = fields.Boolean(string="Pills", )
    alcohol = fields.Boolean(string="Alcohol", )

    # pysical examination
    general_appearance = fields.Text(string="General appearance", )
    constitution = fields.Char(string="Constitution", )
    height = fields.Float(string="Height", )
    weight = fields.Float(string="Weight ", )
    sclap = fields.Char(string="Sclap", )
    cervical_lym_nodes = fields.Char(string="Cervical lymph nodes")
    eyes_gen = fields.Char(string="Eyes General", )
    vision = fields.Char(string="Vision", )
    without_glass = fields.Char(string="Without Glass", )
    with_glass = fields.Char(string="With Glass", )
    color_vision = fields.Char(string="Color Vision", )
    near_vision = fields.Char(string="Near Vision", )
    ears = fields.Char(string="Ears", )
    mouth = fields.Char(string="Mouth", )
    teeth = fields.Char(string="Teeth", )
    decayed = fields.Char(string="Decayed", )
    missing = fields.Char(string="Missing", )
    filled = fields.Char(string="Filled", )
    other_abnoramality = fields.Char(string="Other Abnoramality", )
    trechea = fields.Text('Trachea')
    tongue = fields.Char(string="Tongue", )
    upper_limbs = fields.Char(string="Upper Limbs", )
    pulse = fields.Char(string="Pulse", )
    b_p = fields.Char('B.P')
    chest_gen = fields.Char('Chest General')
    lungs = fields.Char(string="Lungs", )
    heart = fields.Char(string="Heart", )
    abdomen_gen = fields.Char(string="Abdomen General", )
    liver = fields.Char(string='Liver')
    spleen = fields.Char(string="Spleen", )
    other_masses = fields.Char(string="Other Masses", )
    fluid = fields.Char(string="Fluid", )
    hernia = fields.Char(string="Hernia", )
    genitalia = fields.Char(string="Genitalia", )
    lower_limbs = fields.Char(string="Lower Limbs", )
    # investigation
    stol_gen_reaction = fields.Char(string="Stool general Reaction", )
    mucus = fields.Char(string="Mucus", )
    blood = fields.Char(string="Blood", )
    parasites = fields.Char(string="Parasites", )
    concetration = fields.Char(string="Concetration", )
    sp_gravity = fields.Char(string="S.P Gravity", )
    Reaction = fields.Char(string="Reaction", )
    pus_cell = fields.Char(string="Pus cells", )
    rbc = fields.Char(string="R.B.c", )
    casts = fields.Char(string="Casts", )
    ova = fields.Char(string="Ova", )
    x_ray = fields.Char(string="X-Ray", )
    # blood
    hb = fields.Char(string="HB", )
    b_rbc = fields.Char(string="R.B.C", )
    wbc = fields.Char(string="W.B.C", )
    blood_total = fields.Char(string="Total", )
    mantoux_test = fields.Char(string="Mantoux Test", )
    other_investigation = fields.Text(string="Other Investigation", )
    blood_total = fields.Char(string="Total", )
    intelligence = fields.Char(string="Intelligence", )
    speech = fields.Char(string="Speech", )
    cranial_nerves = fields.Char(string="Cranial nerves", )
    motor_sys = fields.Char(string="Motor System", )
    sensor_sys = fields.Char(string="Sensory System", )
    reflex = fields.Char(string="Reflexes", )
    skin = fields.Char(string="Skin", )
    ex_comment = fields.Text(string="Examination Comment", )

    def action_approve(self):
        self.write({
            'doctor_decision': 'approve'
        })

    def action_reject(self):
        self.write({
            'doctor_decision': 'not_approve'
        })


class Surgery(models.Model):
    _name = 'surgery'
    _description = 'medical operation'

    name = fields.Char(string='Name')
    Date = fields.Date(string="Date", )
