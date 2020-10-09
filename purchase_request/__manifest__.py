# -*- coding: utf-8 -*-

{
    'name': 'Purchase Request',
    'version': '13.0.0.8',
    'summary': 'Purchase Request',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'license': "AGPL-3",
    'website': 'http://www.prixgen.com',
    'description': """
        This module helps to create Pruchase Request.
    """,
    'category': "Purchase Management",
    'depends': ['purchase',],

    "data": [
        "security/purchase_request.xml",
        "security/ir.model.access.csv",
        "data/purchase_request_seq.xml",
        "data/purchase_request_demo_data.xml",
        "views/purchase_request_view.xml",
        "reports/report_purchaserequests.xml",
        "views/purchase_request_report.xml",
        "views/mo_request.xml",
        "views/logs_view.xml",
    ],
    'images': ['static/description/icon_image.png'],

    'installable': True,
    'auto_install': False,
    'application': True,
}
