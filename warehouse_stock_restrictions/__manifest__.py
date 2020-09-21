# -*- coding: utf-8 -*-

{
    'name': "Warehouse Restrictions",

    'summary': """
         Warehouse and Stock Location Restriction on Users.""",

    'description': """
        This Module Restricts the User from Accessing Warehouse and Process Stock Moves other than allowed to Warehouses and Stock Locations.
    """,

    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'category': 'Warehouse',
    'version': '13.0.1.2',
    'depends': ['base', 'stock'],

    'data': [

        'users_view.xml',
        'security/security.xml',
        # 'security/ir.model.access.csv',
    ],
    
    
}
