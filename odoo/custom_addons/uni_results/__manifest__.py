# -*- coding: utf-8 -*-

{
    'name': "Students Examination and Results",
    'summary': """
    """,
    'description': """
    """,
    'author': 'itmayin',
    'website': 'http://www.yourcompany.edu',
    'version': '0.0.1',
    'depends': ['mail','uni_admission','uni_services','violations_punishments','timetable'],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/degree_component.xml',
        'views/grade_configration_view.xml',
        'views/res_config_view.xml',
        'views/curriculum_view.xml',
        'views/exam_record_view.xml',
        'views/exam_attendees_view.xml',
        'views/exam_view.xml',
        'views/exam_template_view.xml',
        'views/result_record_view.xml',
        'views/marksheet_view.xml',
        'views/marksheet_line_view.xml',
        'views/student_view.xml',
        'views/exam_types_view.xml',
    ],
    'demo': [],
}
