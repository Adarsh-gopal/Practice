# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ItemGroup(models.Model):
    _name = "item.group"
    _description = "Item Group"
    _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]

    name = fields.Char()
    code = fields.Char()


class ProductGroup1(models.Model):
    _name = "product.group.1"
    _description = "Product Group 1"
    _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]

    name = fields.Char()
    code = fields.Char()


class ProductGroup2(models.Model):
    _name = "product.group.2"
    _description = "Product Group 2"
    _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]

    name = fields.Char()
    code = fields.Char()
    product_group_1 = fields.Many2one('product.group.1')

class ProductGroup3(models.Model):
    _name = "product.group.3"
    _description = "Product Group 3"
    _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]

    name = fields.Char()
    code = fields.Char()
    product_group_2 = fields.Many2one('product.group.2')



class ProductTemplate(models.Model):
    _inherit = "product.template"

    item_group = fields.Many2one('item.group', ondelete='restrict')
    product_group_1 = fields.Many2one('product.group.1', ondelete='restrict')
    product_group_2 = fields.Many2one('product.group.2', domain="[('product_group_1', '=', product_group_1)]", ondelete='restrict')
    product_group_3 = fields.Many2one('product.group.3', domain="[('product_group_2', '=', product_group_2)]", ondelete='restrict')


class StockQuant(models.Model):
    _inherit = "stock.quant"

    item_group = fields.Many2one('item.group',related='product_id.product_tmpl_id.item_group', store=True)
    product_group_1 = fields.Many2one('product.group.1',related='product_id.product_tmpl_id.product_group_1',store=True)
    product_group_2 = fields.Many2one('product.group.2',related='product_id.product_tmpl_id.product_group_2',store=True)
    product_group_3 = fields.Many2one('product.group.3',related='product_id.product_tmpl_id.product_group_3',store=True)


class StockMove(models.Model):
    _inherit = "stock.move"

    item_group = fields.Many2one('item.group',related='product_id.product_tmpl_id.item_group', store=True)
    product_group_1 = fields.Many2one('product.group.1',related='product_id.product_tmpl_id.product_group_1',store=True)
    product_group_2 = fields.Many2one('product.group.2',related='product_id.product_tmpl_id.product_group_2',store=True)
    product_group_3 = fields.Many2one('product.group.3',related='product_id.product_tmpl_id.product_group_3',store=True)


class StockMove(models.Model):
    _inherit = "stock.move.line"

    item_group = fields.Many2one('item.group',related='product_id.product_tmpl_id.item_group', store=True)
    product_group_1 = fields.Many2one('product.group.1',related='product_id.product_tmpl_id.product_group_1',store=True)
    product_group_2 = fields.Many2one('product.group.2',related='product_id.product_tmpl_id.product_group_2',store=True)
    product_group_3 = fields.Many2one('product.group.3',related='product_id.product_tmpl_id.product_group_3',store=True)