# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from dateutil.relativedelta import relativedelta

class FleetVehicleLogFuel(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    indent_ref = fields.Char(string="Indent Reference")

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    z_engine_no = fields.Char(string="Engine No")

class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    z_policy_no = fields.Char(string="Policy No")