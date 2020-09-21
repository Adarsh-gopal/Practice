# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Partner(models.Model):
    _inherit = 'purchase.order'

    scheduled_dispatch_date = fields.Datetime()