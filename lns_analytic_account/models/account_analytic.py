# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import ValidationError

class AccountAnalyticAccount(models.Model):
	_inherit = 'account.analytic.account'

	z_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
	z_sale_lead = fields.Many2one('res.users', string="Sales Lead")
	z_delivery_lead = fields.Many2one('res.users', string="Delivery Lead")

class AccountAnalyticTags(models.Model):
	_inherit = 'account.analytic.tag'


	z_user_id = fields.Many2one('res.users', string="Primary Salesperson")


