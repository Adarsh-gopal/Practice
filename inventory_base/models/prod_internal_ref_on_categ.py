# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductCategory(models.Model):
    _inherit = "product.category"

    internal_reference_sequence_id = fields.Many2one('ir.sequence')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self,vals):
        sequence = self.env['product.category'].browse(vals.get('categ_id')).internal_reference_sequence_id
        if sequence:
            vals['default_code'] = sequence.next_by_id()
        
        return super(ProductTemplate,self).create(vals)