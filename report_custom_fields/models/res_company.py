from odoo import api, fields, models,_


class ResCompany(models.Model):
	_inherit="res.company"
	cin_no = fields.Char(string="CIN No.",store=True)
	tan_no = fields.Char(string="TAN No.",store=True)
	pan_no = fields.Char(string="PAN No.",store=True)
	factory_reg_no = fields.Char(string="Factory Registration No.",store=True)
	

	