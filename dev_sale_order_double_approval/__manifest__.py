

{
    'name': 'Sale Double Approval Process Workflow',
    'version': '13.11',
    'sequence': 1,
    'category': 'Generic Modules/Sales Management',
    'description':
        """
        This module helps you to set limits on Sale Orders, So, Manager must have validate Sale Order if it exceed the Per-Defined Limit before Confirmation.
         
         Sale Double Approval, Double Approval, Approval Process, Sale Approval, Approval workflow , Approval sale, two lavel process, two way approval, 
         
Sale Double Approval Process Workflow
Odoo Sale Double Approval Process Workflow
Sale double approval process
Odoo sale double approval process
Sales double approval 
Odoo sales double approval
Sales double approval process
Odoo sales double approval process
Sale approval workflow
Odoo sale approval workflow
Sale approval workflow odoo app
Sale approval workflow odoo apps
Double Approval process Workflow into sale order screen
Odoo Double Approval process Workflow into sale order screen
Set Two Step Verification on Sale Orders
Odoo Set Two Step Verification on Sale Orders
Set a limit amount on Sale Order as Two Step Verification
Odoo Set a limit amount on Sale Order as Two Step Verification
Tripple Approval Sales
Odoo Tripple Approval Sales
Sale order approval process
Odoo sale order approval process
         
    """,
    'summary': 'odoo app Allow you to Double Approval process Workflow into sale order',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['base', 'sale_management','product','sale_stock',],
    'data': [
        'security/security.xml',
        'views/res_config_settings_views.xml',
        'views/sale_order_view.xml',
    ],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

