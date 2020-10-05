# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

# -*- coding: utf-8 -*-

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

class WeighmentPickingType(models.Model):
    _name = "weighment.picking.type"
    _description = "Weighment Picking Type"
   
    name = fields.Char(string="Weighment Type",required=True)
    description = fields.Char(string="Description")

    count_picking_ready = fields.Integer(compute='_compute_picking_count_weighment')

    def _compute_picking_count_weighment(self):
        # TDE TODO count picking can be done using previous two
        domains = {

            'count_picking_ready': [('state', '=', 'open')],

        }
        for field in domains:
            data = self.env['weighment.picking'].read_group(domains[field] +
                [('state', '=', ('open')), ('weighment_type', 'in', self.ids)],
                ['weighment_type'], ['weighment_type'])
            count = {
                x['weighment_type'][0]: x['weighment_type_count']
                for x in data if x['weighment_type']
            }
            for record in self:
                record[field] = count.get(record.id, 0)

    def _get_action(self, action_xmlid):
        # TDE TODO check to have one view + custo in methods
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['display_name'] = self.display_name
        return action


    def get_weighment_picking_action_picking_type(self):
        return self._get_action('weighment.weighment_picking_action_picking_type')


    def get_action_weighment_picking_tree_ready(self):
        return self._get_action('weighment.action_weighment_picking_tree_ready')

