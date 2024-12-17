# -*- coding: utf-8 -*-
##############################################################################
#
#    UOFK,
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Base Custom",
    'summary': """
    """,
    'description': """
    """,
    'author': 'itmayin',
    'website': 'http://www.yourcompany.com',
    'category': 'Base',
    'version': '0.0.1',
    'depends': ['base', 'mail'],
    'data': [
        # 'security/ir.model.access.csv',
        #'data/l10n_generic_coa_uofk_Structure_data.xml',
		'data/state.xml',
        'views/company_views.xml',
        'report/reports_header.xml',
    ],
    'demo': [],
}
