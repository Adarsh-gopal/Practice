# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    item_group = fields.Many2one('item.group',related='product_id.product_tmpl_id.item_group', store=True)
    product_group_1 = fields.Many2one('product.group.1',related='product_id.product_tmpl_id.product_group_1',store=True)
    product_group_2 = fields.Many2one('product.group.2',related='product_id.product_tmpl_id.product_group_2',store=True)
    product_group_3 = fields.Many2one('product.group.3',related='product_id.product_tmpl_id.product_group_3',store=True)


# class AccountInvoiceReport(models.Model):
#     _inherit = "account.invoice.report"

#     item_group = fields.Many2one('item.group')
#     product_group_1 = fields.Many2one('product.group.1')
#     product_group_2 = fields.Many2one('product.group.2')
#     product_group_3 = fields.Many2one('product.group.3')

#     def _select(self):
#         return super(AccountInvoiceReport, self)._select() + ", move.item_group as item_group"

#     def _group_by(self):
#         return super(AccountInvoiceReport, self)._group_by() + ", move.item_group"