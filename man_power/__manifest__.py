{
    'name': "Man Power",
    'version': '13.1',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Tool',
    'installable': True,
    'application': True,
    'depends': ['base','mrp','resource','hr'],
    'data': [
        'data/report_paperformat.xml',
        'views/manpower.xml',
        'views/man_attendance.xml',
        'views/roster.xml',
        
        'report/man_power.xml',
        'report/man_power_template.xml',
        ], 
        'images': ['static/description/icon.png'],
}

