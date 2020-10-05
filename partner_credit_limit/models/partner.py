# See LICENSE file for full copyright and licensing details.

from odoo import fields,api, models,_
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    over_credit = fields.Boolean('Allow Over Credit?')

    
