{
    'name': 'Gate Entry',
    'version': '13.1',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Security',
    'summary': " Gate Entry  ",
    'description': """
        Gate Entry Module captures Inward and Outward movement of vehicles.
    """,
    'depends': ['sale_management','sale','purchase','stock','fleet','account'],
    'images': ['static/description/Banner.png'],
    'data': [
        'views/account_invoice_views.xml',
        'views/fleet_vehicle_log_contract.xml',
    	'views/inward_view.xml',
    	'views/outward_view.xml',
        'views/warehouse_employee.xml',
    	'views/operation_type.xml',
    	'data/ir_sequence_data.xml',
    	'views/inward_button.xml',
    	'views/outward_button.xml',
        'security/groups.xml',
        'security/ir.model.access.csv'
    	],
    'auto_install': False,
    'application': True,

}

