# -*- coding: utf-8 -*-


{
    'name': 'Purchase Register Report',
    'version': '13.5',
    'category': 'Purchase',
    'summary': 'Purchase Register Report',
    'description': """
		This module get the Purchase summary between the given dates .
    				""",
    'author': "Prixgen tech Solutions",
    'depends': ['hr', 'purchase','stock','product'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/stock_picking_views.xml',
        'wizard/purchase_register_report_view.xml',
    ],

    'installable': True,
    'auto_install': False
}
