# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_
from datetime import datetime , date
from odoo.exceptions import ValidationError, AccessError, UserError, RedirectWarning, Warning


class resetdraft(models.Model):
	_inherit = 'account.move'


	def button_resetdraft(self):
		for record in self:
			if record.state == 'posted':
				record.button_draft()
			else:
				raise ValidationError(_("{} invoice is not in posted state".format(record.name)))


	def button_removeentry(self):
		print(self)
		for entry in self:
			if entry.state == 'draft':
				entry.name = '/'
			else:
				raise ValidationError(_("{} invoice is not in draft state".format(record.name)))