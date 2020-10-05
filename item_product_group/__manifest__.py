{
    'name': 'Product Categories & Groups',
    'version': '13.0',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Products',
    'depends': ['base', 'purchase','product'],
    'description': """ Item category and product group code""",
    'data': [
        'views/item_category_view.xml',
        'views/product_category_secondary_view.xml',
        'views/product_group_primary_view.xml',
        'views/product_template.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
