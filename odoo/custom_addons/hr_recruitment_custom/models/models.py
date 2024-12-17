# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrJobTitle(models.Model):
    _name = "hr.job.title"

    name = fields.Char("Name")
    job_id = fields.Many2one("hr.job", string="Main Job")


class HrJob(models.Model):
    _inherit = "hr.job"

    job_title_ids = fields.One2many("hr.job.title", "job_id", string="Jobs")
    program_ids = fields.Many2many("uni.faculty.program", "job_program_rel" ,string="Programs")


class HrApplicant(models.Model):
    _inherit = "hr.applicant"


    job_title_id = fields.Many2one("hr.job.title", string="Applied Job")
    program_id = fields.Many2one("uni.faculty.program", string="Program")
    gender = fields.Selection([('male','Male'),('female','Female')], string="Gender")
    age = fields.Selection([('18','18-22'),('23','23-27'),('28','28-32'),('32','More than 32')], string="Age")
    phone2 = fields.Char("Phone Number 2")
    city = fields.Selection([('khartoum','Khartoum'),('bahri','Bahri'),('omdurman','Omdurman')], string="City")
    address = fields.Text("Address")
    university = fields.Char("University")
    street = fields.Char("Street")
    college = fields.Char("College")
    major_field = fields.Char("Major Field")
    neighborhood = fields.Char("Neighborhood")
    grade = fields.Selection([('a','Exellent'),('b','V. Good / جيد جدا'),('c','Good / جيد'),('d','Acceptable / مقبول')], string="Grade")
    experience = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('more','More than 5')], string="Experience Years")
    degree = fields.Selection([
        ('primary','Primary / أساس'),('secondary','Secondary / ثانوي'),
        ('diploma','Diploma / دبلوم'),('bachler','Bachler\'s / بكالريوس'),('master','Master  / ماجستير'),('phd','PhD  / دكتوراة')], string="Degree")
    selected_job = fields.Selection([('1','وظائف عمالية'),('2','موظف موارد بشرية'),('3','موظف قبول'),('4','موظف تسجيل'),('5','موظف سلامة و متابعة'),
                                    ('6','موظف جودة'),('7','موظف احصاء وامتحانات'),('8','مهندس تقنية معلومات وكمبيوتر'),('9','مبرمج Odoo Developer'),('10','موظف مراجعة داخلية'),
                                    ('11','موظف محاسبة'),('12','موظف شئون ادارية'),('13','موظف سكرتارية'),('14','موظف أمن وسلامة ( استقبال )'),('15','موظف أمن وسلامة ( حرس أمني )'),
                                            ], string="Job")
    eng_level = fields.Selection([('nothing','Nothing'),('begineer','Begineer'),('intermediate','Intermediate'),('professional','Professional')], string="English language level")
    computer_level = fields.Selection([('nothing','Nothing'),('begineer','Begineer'),('intermediate','Intermediate'),('professional','Professional')], string="Experience in dealing with computers and devices")
    microsoft_level = fields.Selection([('nothing','Nothing'),('begineer','Begineer'),('intermediate','Intermediate'),('professional','Professional')], string="Experience working with Microsoft Office")
    pdf_level = fields.Selection([('nothing','Nothing'),('begineer','Begineer'),('intermediate','Intermediate'),('professional','Professional')], string="Experience working with PDF")
    excel_level = fields.Selection([('nothing','Nothing'),('begineer','Begineer'),('intermediate','Intermediate'),('professional','Professional')], string="Experience working with Excel")
    excel_advance_level = fields.Selection([('nothing','Nothing'),('begineer','Begineer'),('intermediate','Intermediate'),('professional','Professional')], string="Experience working with Excel (Advanced)")
    e_learn_level = fields.Selection([('nothing','Nothing'),('begineer','Begineer'),('intermediate','Intermediate'),('professional','Professional')], string="Do you have experience working with e-learning platforms?")
    email_level = fields.Selection([('nothing','Nothing'),('begineer','Begineer'),('intermediate','Intermediate'),('professional','Professional')], string="Do you have experience dealing with email?")