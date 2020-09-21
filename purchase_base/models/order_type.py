# -*- coding: utf-8 -*-

from odoo import models, api, fields,_


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    order_type = fields.Many2one('purchase.order.type')


class OrderType(models.Model):
    _name = 'purchase.order.type'
    _description = 'Order Type'

    name = fields.Char()
    description = fields.Char()