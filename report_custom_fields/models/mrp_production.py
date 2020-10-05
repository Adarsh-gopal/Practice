from odoo import models, fields, api, _

class MrpProduction(models.Model):
	_name = "mrp.production"
	_inherit = "mrp.production"
	order_type = fields.Many2one('mrp.production.type',string='Order Type',store=True)
	
class MrpProductionType(models.Model):
	_name = "mrp.production.type"
	name= fields.Char(store=True ,ondelete='cascade')
	description= fields.Text(string='Description',store=True ,ondelete='cascade')