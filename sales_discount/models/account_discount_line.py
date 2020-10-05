import uuid

from itertools import groupby
from datetime import datetime, timedelta
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

from odoo.tools.misc import formatLang

from odoo.addons import decimal_precision as dp


class AccountDiscountLine(models.Model):
    _name = "account.discount.line"

    @api.depends('invoice_categ_dis_id.invoice_line_ids')
    def _compute_base_invoice_amount_discount(self):
        categ_grouped = {}
        for invoice in self.mapped('invoice_categ_dis_id'):
            categ_grouped[invoice.id] = invoice.get_invoice_product_discount_values()
        for categ_lines in self:
            categ_lines.base = 0.0
            if categ_lines.category:
                key = categ_lines.category.get_grouping_key_categ({
                    'category': categ_lines.category.id,

                })
        
    invoice_categ_dis_id = fields.Many2one('account.move', string='Order Reference', ondelete='cascade', index=True, copy=False)

    name = fields.Text(string='Description')
    category = fields.Many2one('item.category',string="Category")
    amount = fields.Monetary()
    amount_rounding = fields.Monetary()
    trade_discount_id = fields.Many2one('sale.discount',string="Trade Discount",domain="[('discount_type','=','trade')]")
    trade_discounts = fields.Float(string='Discount (%)', digits=dp.get_precision('Price'), default=0.0)
    trade_amount = fields.Float('Amount', digits=dp.get_precision('Price'), default=0.0,store=True,compute="_compute_discounts",track_visibility='always')
    quantity_discount_id = fields.Many2one('sale.discount',string="Quantity Discount",domain="[('discount_type','=','quantity')]")
    quantity_discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Price'), default=0.0)
    quantity_amount = fields.Float('Amount', digits=dp.get_precision('Price'), default=0.0,store=True,compute="_compute_discounts",track_visibility='always')
    special_discount_id = fields.Many2one('sale.discount',string="Special Discount",domain="[('discount_type','=','special')]")
    special_discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Price'), default=0.0)
    special_amount = fields.Float('Amount', digits=dp.get_precision('Price'), default=0.0,store=True,compute="_compute_discounts",track_visibility='always')
    currency_id = fields.Many2one('res.currency', related='invoice_categ_dis_id.currency_id', store=True, readonly=True)

    base = fields.Monetary(string='Base', compute='_compute_base_invoice_amount_discount', store=True)
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of invoice tds.")
    manual = fields.Boolean(string="Manual")



    @api.depends('amount','trade_discounts','quantity_discount','special_discount')
    def _compute_discounts(self):
        for line in self:
            line.trade_amount = (line.amount * line.trade_discounts)/100
            line.quantity_amount = ((line.amount - line.trade_amount) * line.quantity_discount)/100
            line.special_amount = (((line.amount - line.trade_amount)-line.quantity_amount) * line.special_discount)/100

 