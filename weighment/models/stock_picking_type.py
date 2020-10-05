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


class PickingType(models.Model):
    _inherit = "stock.picking.type"
    _description = "The operation type determines the picking view"
    _order = 'sequence, id'

    weighment_type = fields.Many2one('weighment.picking.type',string="Weighment Type")

