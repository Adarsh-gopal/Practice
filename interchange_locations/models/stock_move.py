from odoo import api, fields, models,_
from odoo.exceptions import AccessError, UserError,ValidationError





class StockPickingType(models.Model):
	_inherit='stock.picking.type'


	interchange= fields.Boolean("Repacking")


class StockPicking(models.Model):
	_inherit='stock.picking'


	chnage_location= fields.Boolean("Repacking",compute='get_repacking',store=True)


	@api.depends('picking_type_id')
	def get_repacking(self):
		for l in self:
			if l.picking_type_id.interchange:
				l.chnage_location = True
			else:
				l.chnage_location = False


class StockMove(models.Model):
	_inherit='stock.move.line'


	chnage_locations= fields.Boolean("Repacking")


	@api.onchange('chnage_locations')
	def change_location_ids(self):
		if self.picking_id.picking_type_id.interchange and self.chnage_locations:
			self.location_id = self.picking_id.location_dest_id.id
			self.location_dest_id = self.picking_id.location_id.id
		







