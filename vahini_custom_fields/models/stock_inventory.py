from odoo import api, fields, models,_
class StockInventoryReason(models.Model):
	_name="stock.inventory.reason"

	name = fields.Char(string="Reason")

class StockInventory(models.Model):
	_inherit="stock.inventory"
	z_reason = fields.Many2one('stock.inventory.reason',string="Reason") 

class StockPicking(models.Model):
	_inherit="stock.picking"

	z_vehicle = fields.Char(string='External Vehicle NO')

