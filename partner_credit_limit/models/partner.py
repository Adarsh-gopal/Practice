# See LICENSE file for full copyright and licensing details.

from odoo import fields,api, models,_
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta

class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_term = fields.Integer('Additional Credit Days')
    # next_commitment = fields.Date('Next Payment Commitment')

    
