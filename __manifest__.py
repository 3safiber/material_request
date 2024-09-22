# -*- coding: utf-8 -*-
{
    'name': "Material Request",
    'version': '0.1',
    'summary': "Material Request",

    'description': """
      Material Request
    """,

    'author': "Salameh",
    'website': "",

    'category': 'Sales',

    'depends': ['base', 'contacts', 'stock', 'hr', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizard/report_wizard.xml',
        'views/material_request_view.xml',
        'reports/material_request_report.xml',
    ],
    'demo': [],
    'application': True,
    'sequence': 3
}
