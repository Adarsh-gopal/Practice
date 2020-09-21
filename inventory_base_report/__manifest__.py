# -*- coding: utf-8 -*-
{
    'name': 'Inventory Base Report',
    'version': '13.0.6',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Inventory',
    'description': """
Creating the one custom table to find the opening and closing stock	
""",
    'depends': ['stock','stock_account','tansit_location'],

    'data': [
        'security/ir.model.access.csv',
        'views/inventory_base_report_view.xml',
    ],
    'application': False,
    'installable': True,
}
