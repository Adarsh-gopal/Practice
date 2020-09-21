# -*- coding: utf-8 -*-
{
    'name': "Alt Product Code",

    'summary': """
        Alt Product Code""",

    'description': """
        Alt Product Code
    """,
    
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",
    
    'category': 'Inventory',
    'version': '13.0.2.3',
    
    'depends': ['stock','product'],
    
    'data': [
        # 'security/ir.model.access.csv',
        'security/alt_prod_code_user_group.xml',
        'views/product_template.xml',
        'views/product_product.xml'
    ],
}
