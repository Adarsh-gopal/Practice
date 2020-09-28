
{
    'name': 'Material Requisition',
    'summary': """Material Requisition Creation""",
    'description': """On creation of the manufacturing order , raw material availability is checked and indent is raised automatically with the approval process""",
    'version': '13.9',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Inventory',
    'depends': ['base','stock','sale','mrp','account','lns_analytic_account'],
    'license': 'LGPL-3',
    'data': [
        'security/config_settings.xml',
        'security/ir.model.access.csv',
        #'views/inventory_indent.xml',
        'views/mrp_indent.xml',
        'views/mrp_indent_active.xml',
        'views/scrap_order.xml',
        'data/ir_sequence_data.xml',
        'views/manufacturing_plan_view.xml',
        'views/res_config_settings.xml',
    ],
    'images': ['static/description/download.png'],
    
    'installable': True,
    'auto_install': False,
}
