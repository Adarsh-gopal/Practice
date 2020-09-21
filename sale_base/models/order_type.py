# -*- coding: utf-8 -*-

from odoo import models, api, fields,_


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_type = fields.Many2one('sale.order.type')


class OrderType(models.Model):
    _name = 'sale.order.type'
    _description = 'Order Type'

    name = fields.Char()
    description = fields.Char()