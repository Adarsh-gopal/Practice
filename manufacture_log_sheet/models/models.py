# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class manufacture_log_sheet(models.Model):
#     _name = 'manufacture_log_sheet.manufacture_log_sheet'
#     _description = 'manufacture_log_sheet.manufacture_log_sheet'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
