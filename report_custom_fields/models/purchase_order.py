from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	ext_doc_num = fields.Char(string='External po number', store=True)
	order_type = fields.Many2one('purchase.order.type',string='Order Type',store=True)
	remark=fields.Text('Remark')
	
class PurchaseOrderType(models.Model):
	_name = 'purchase.order.type'
	name= fields.Char(store=True ,ondelete='cascade')
	description= fields.Text(string='Description',store=True ,ondelete='cascade')

	