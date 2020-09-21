# -*- encoding: utf-8 -*-
{
    'name' : 'SW - RFQ Separate Sequence',
    'version' : '13.0.2.0',
    'category' : 'Purchase',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'license':  "Other proprietary",
    'summary': """Add a special sequence to your RFQs""",
    'data': ['sequence.xml','po.xml',],
    'depends' : ['base', 'purchase','stock'],
    'images':  ["static/description/image.png"],
    'installable': True,
    'auto_install': False,
}