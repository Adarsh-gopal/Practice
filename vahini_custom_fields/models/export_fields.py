from odoo import api, fields, models



class PortOrder(models.Model):
	_name = 'port.order'

	name = fields.Char('Name')
	city = fields.Char('City')
	country = fields.Many2one('res.country','Country')

class ExportShipment(models.Model):
	_name = 'export.shipment'
	
	name = fields.Char('Name')

class ContainerType(models.Model):
	_name = 'type.container'
	name = fields.Char('Name')
