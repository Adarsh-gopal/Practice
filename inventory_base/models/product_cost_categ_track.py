# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    standard_price = fields.Float(track_visibility='always')
    categ_id = fields.Many2one(track_visibility='always')

    @api.onchange('categ_id')
    def _validate_categ_changer(self):
        if self.categ_id and not self.env.user.has_group('inventory_base.group_prod_categ_change'):
            raise ValidationError(_("""Sorry,
You do not have access to change the Product Category"""))