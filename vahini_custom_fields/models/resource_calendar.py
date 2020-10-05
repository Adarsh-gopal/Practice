from odoo import api, fields, models,_

class ResourceCalendar(models.Model):
	_inherit="resource.calendar"
	z_production_schedule = fields.Boolean(string="Production Schedule") 

