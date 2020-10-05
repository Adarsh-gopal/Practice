# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.move'
    weighment_status = fields.Boolean(string="Weighment status",default=False)