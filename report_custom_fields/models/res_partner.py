from odoo import api, fields, models,_


class ResPartner(models.Model):
	_inherit="res.partner"
	gst_reg_type = fields.Selection([('registered','Registered'),('unregistered','Unregistered'),('composite','Composite')], default='registered',string="GST Registration Type")
	

	