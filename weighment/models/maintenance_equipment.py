from odoo import models, fields, api, _, exceptions


class Equipments(models.Model):
	_inherit = "maintenance.equipment"
	
	weight = fields.Integer(string="Weight")

class Fleet(models.Model):
	_inherit = "fleet.vehicle"
	
	weight = fields.Integer(string="Weight")