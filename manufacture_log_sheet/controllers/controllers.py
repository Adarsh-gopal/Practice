# -*- coding: utf-8 -*-
# from odoo import http


# class ManufactureLogSheet(http.Controller):
#     @http.route('/manufacture_log_sheet/manufacture_log_sheet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/manufacture_log_sheet/manufacture_log_sheet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('manufacture_log_sheet.listing', {
#             'root': '/manufacture_log_sheet/manufacture_log_sheet',
#             'objects': http.request.env['manufacture_log_sheet.manufacture_log_sheet'].search([]),
#         })

#     @http.route('/manufacture_log_sheet/manufacture_log_sheet/objects/<model("manufacture_log_sheet.manufacture_log_sheet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('manufacture_log_sheet.object', {
#             'object': obj
#         })
