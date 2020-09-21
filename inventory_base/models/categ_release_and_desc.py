# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductCategory(models.Model):
    _inherit = "product.category"

    description = fields.Char('Description')
    release = fields.Boolean('Release')

class ProductTemplate(models.Model):
    _inherit = "product.template"

    categ_id = fields.Many2one(default=False,domain=[('release', '=', 'True')])