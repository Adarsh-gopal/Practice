# -*- coding: utf-8 -*-

from collections import Counter

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
# from odoo.tools.pycompat import izip
from odoo.tools.float_utils import float_round, float_compare, float_is_zero

class StockMove(models.Model):
    _inherit = "stock.move"

    z_supplier_rate = fields.Float(string="Supplier Rate")

    # @api.onchange('z_supplier_rate')
    # def validate_supplier_rate()