# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    alt_code = fields.Char(
        'Alternate Reference', compute='_compute_alt_code',
        inverse='_set_alt_code', store=True)

    @api.depends('product_variant_ids', 'product_variant_ids.alt_code')
    def _compute_alt_code(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.alt_code = template.product_variant_ids.alt_code
        for template in (self - unique_variants):
            template.alt_code = False

    def _set_alt_code(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.alt_code = template.alt_code

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(ProductTemplate, self).create(vals_list)

        for template, vals in zip(templates, vals_list):
            related_vals = {}

            if vals.get('alt_code'):
                related_vals['alt_code'] = vals['alt_code']

            if related_vals:
                template.write(related_vals)

        return templates



    def name_get(self):
        res = super(ProductTemplate, self).name_get()
        if self.env.user.has_group('alternate_product_code.alt_code_user'):
            self.browse(self.ids).read(['name', 'alt_code'])
            return [(template.id, '%s%s' % (template.alt_code and '[%s] ' % template.alt_code or '', template.name))
                    for template in self]
        else:
            return res
