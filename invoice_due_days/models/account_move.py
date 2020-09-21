# See LICENSE file for full copyright and licensing details.

from odoo import fields,api, models,_
from datetime import datetime,date,timedelta
import pdb

class AccountMove(models.Model):
    _inherit = 'account.move'

    # over_credit = fields.Boolean('Allow Over Credit?')
    due_no_of_days = fields.Integer("Overdue Days",compute='get_days')
    invoice_age_days = fields.Integer("Invoice Age Days",store=True,track_visibility='always'
        ,compute='get_invoice_days')
    z_payment_date = fields.Date('Date')
    


    @api.depends('invoice_payment_state')
    def get_days(self):
        for l in self:
            if l.invoice_payment_state !='paid':
                if l.invoice_date_due and l.type == 'out_invoice':
                    # print("ddddddddddddddddddddddddddddddddd",l.invoice_date_due)
                    l.due_no_of_days = -(l.invoice_date_due - date.today()).days
                    #print(l.due_no_of_days,'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                else:
                    l.due_no_of_days = 0
            else:
                l.due_no_of_days = 0
        return True

    @api.depends('invoice_date')
    def get_invoice_days(self):
        for l in self:
            if l.invoice_date:
                if l.type == 'out_invoice':
                    l.invoice_age_days = (date.today() - l.invoice_date).days
                    #print(l.invoice_age_days,l.invoice_date,date.today(),'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                else:
                    l.invoice_age_days = 0
            else:
                l.invoice_age_days = 0
        return True
