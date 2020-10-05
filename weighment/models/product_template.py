from odoo import models, fields, api, _, exceptions

class ProductTemplate(models.Model):
	_inherit = "product.template"

	tolerance = fields.Float(string="Tolerance")


