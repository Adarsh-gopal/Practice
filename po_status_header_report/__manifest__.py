{
    'name': 'Purchase Order Header Status  Report',
    
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',  
    
    'version': '13.2',
    
    'category': 'Purchase',

    'summary': 'This module is useful to show the purchase order status whether  completely or partially invoiced',

    'description': """This module is useful to show the purchase order status whether  completely or partially invoiced""",
    
    'depends': ['purchase'],
    
    'data': [
        'views/purchase_order.xml',
    ],
    
    'auto_install': False,
    'installable' : True,
    'application': True,
}
