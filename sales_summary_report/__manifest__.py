# -*- coding: utf-8 -*-


{
    'name': 'Sales Register Report',
    'version': '13.10',
    'category': 'Sales',
    'summary': 'Sales Summary Report',
    'description': """
		This module get the sales summary between the given dates .
    				""",
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'depends': ['hr', 'sale','account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sales_register_view.xml',
    ],

    'installable': True,
    'auto_install': False
}
