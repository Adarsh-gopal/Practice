# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import namedtuple
import json
import time

from itertools import groupby
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter

class Picking(models.Model):
	_inherit = "stock.picking"
	_order = "name desc" 
	weighment_id = fields.Many2one('weighment.picking',string='Attach Weighment No')

class StockMove(models.Model):
    _inherit = "stock.move"

    stock_line_id = fields.One2many('weighment.product', 'deliver_line_id', string="stock move id", readonly=True, copy=False)