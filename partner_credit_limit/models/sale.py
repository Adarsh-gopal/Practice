# See LICENSE file for full copyright and licensing details.


from odoo import api, fields,models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta,date


class SaleOrder(models.Model):
    _inherit = "sale.order"

    allow_credit = fields.Boolean('Allow Over Credit?')

    
    def check_limit(self):
        self.ensure_one()
        partner = self.partner_id
        user_id = self.env['res.users'].search([
            ('partner_id', '=', partner.id)], limit=1)
        if user_id and not user_id.has_group('base.group_portal') or not \
                user_id:

            moveline_obj = self.env['account.move.line']
            movelines = moveline_obj.search(
                [('partner_id', '=', partner.id),
                 ('account_id.user_type_id.name', 'in',
                  ['Receivable', 'Payable'])]
            )
            confirm_sale_order = self.search([('partner_id', '=', partner.id),
                                              ('state', '=', 'sale')])
            debit, credit = 0.0, 0.0
            amount_total = 0.0
            for status in confirm_sale_order:
                amount_total += status.amount_total
            for line in movelines:
                credit += line.credit
                debit += line.debit
            due = debit - credit

            if (self.amount_total + due) >= self.partner_id.credit_limit:
                if not partner.over_credit:
                    raise UserError(_("Sales order amount or due amount exceeds credit limit, cannot confirm order"))
            if due >= self.partner_id.credit_limit:
                if not partner.over_credit:
                    raise UserError(_("Sale Order exceeds the credit limit amount %s ,cannot confirm order" %(self.partner_id.credit_limit)))
            return True
           



    
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        user = self.env.user
        if user.sale_order:
            for order in self:
                order.check_limit()
                if order.partner_id.over_credit == False:
                    order.verify_date()
                # if order.partner_id.over_credit == False:
                #     order.check_total_overdue()
        else:
            raise models.ValidationError('You are not authorized to confirm sale')
        return res


    
    @api.constrains('partner_id.total_due')
    def check_total_overdue(self):
        for rec in self:
            if rec.partner_id.total_due > 0:
                raise ValidationError(_("Check the Overdue for Customer %s" %(self.partner_id.name)))
        return True

    
    def verify_date(self):
        partner = self.partner_id
        date = fields.Date.today()
        res = self.env['account.move'].search([('partner_id','=',partner.id),('invoice_date_due','<=',date),('state','=','open')])
        if res:
            raise ValidationError(_("This customer has overdue, cannot confirm sale order"))
        

    


