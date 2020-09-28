from odoo import api, fields, models, _
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta

class CreditInfo(models.TransientModel):
    _name = "credit.info"

    name = fields.Float('Credit Limit for Customer')
    credit_days = fields.Many2one('account.payment.term',string='Credit Days')
    additional_credit_days = fields.Integer('Additional Credit Days')
    total_outstanding_as_on_date = fields.Float('Total Outstanding as on date')
    over_credit_days = fields.Float('Amount Over Credit Days')
    over_credit_limit = fields.Float('Amount Over Credit Limit')
    next_payment_date = fields.Date('Next Payment Commitment Date')
    next_payment_amt = fields.Float('Next Payment Commitment Amount')
    sale_last = fields.Float('Sale Last 30 days')
    collection_last = fields.Float('Collection Last 30 days')
    last_payment = fields.Float('Last Payment amount')
    last_payment_date = fields.Date('Last Payment Date')

    # def process_credit(self):
    # 	context=self._context
    # 	record=self.env['sale.order'].search([('id','=',self._context['parent_obj'])])
    # 	if record:
    # 		for l in record:
    # 			self.name = l.partner_id.credit_limit
