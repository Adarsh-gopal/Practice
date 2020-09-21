# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Man_report(models.Model):
	_inherit = "mrp.production"


	def get_work_orders(self):
		data = self.env['mrp.workorder'].search([('production_id', 'in', self.ids),('state', '=', 'done')])
	
		return data