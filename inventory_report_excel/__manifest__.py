# -*- coding: utf-8 -*-
{
    'name': 'Inventory  Report',
    'version': '13.1.3',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Inventory',
    'description': """
This module generates xlsx reports for Inventory 	
""",
    'depends': ['stock','inventory_base_report'],

    'data': [
        'wizard/inventory_report_view.xml',
    ],
    'application': False,
    'installable': True,
}
