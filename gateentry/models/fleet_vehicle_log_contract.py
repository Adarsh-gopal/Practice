from odoo import models, fields, api, _,exceptions

class FleetServiceType(models.Model):
	_inherit = 'fleet.service.type'

	z_gate_validate = fields.Boolean(string="Validate at Gate", default=False)
