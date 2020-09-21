# -*- coding: utf-8 -*-
{
    'name': 'Inventory Transit Location',
    'version': '13.0.1',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Inventory',
    'description': """
Transit Location for ravago
""",
    'depends': ['stock','stock_account'],

    'data': [
        'views/transit_location_view.xml',
    ],
    'application': False,
    'installable': True,
}
