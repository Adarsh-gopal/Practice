{
    'name': 'LNS Analytic Account',
    'version': '13.34',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Accounting',
    'summary': 'Analytic Account',
    'description': """Developed.P""",
    'depends': ['sale','sale_management','account','mrp','mrp_maintenance','stock',
    'hr','hr_payroll','purchase','account_accountant','analytic','stock_landed_costs',
    'purchase_stock'],
    'data': [
        'views/account_payment_views.xml',
        'views/account_analytic_views.xml',
        'views/account_move_views.xml',
        # 'views/account_invoice_views.xml',
        'views/hr_payroll_account_views.xml',
    	'views/mrp_production_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/stock_inventory_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_landed_cost_views.xml',
        'views/stock_production_lot_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
