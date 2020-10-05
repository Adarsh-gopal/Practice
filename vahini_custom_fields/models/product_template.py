from odoo import api, fields, models, tools, _


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	min_thickness = fields.Float(string="Minimum Thickness")
	max_thickness = fields.Float(string="Maximum Thickness")
	prod_length = fields.Float(string="Length")