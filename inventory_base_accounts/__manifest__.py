# -*- coding: utf-8 -*-
{
    'name': "inventory_base_accounts_1.0",

    'summary': """
        Base Customization On Inventory(stock) dependent on Accounting""",

    'description': """
        Included Functionalities -
            1) Product/Item Groups.----------------(product_groups.py/.xml)
    """,

    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',


    'category': 'Customization',
    'version': '13.0.1.0',

    'depends': ['base','inventory_base','stock_account'],

    'data': [
        'views/product_groups.xml',
    ],
}