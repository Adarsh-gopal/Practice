# See LICENSE file for full copyright and licensing details.


from odoo import api, fields,models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
import pdb
class AccountMove(models.Model):
    _inherit = "account.move"

    # due_date = fields.Date('Credit Limit Due Date',store=True,track_visibility='always',compute='compute_due_date')
    credit_date = fields.Date('Credit Limit Due Date',store=True,track_visibility='always',compute='compute_credit_date')
    credit_last_30_days = fields.Date('Last 30 Days')
    

    @api.depends('invoice_date_due')
    def compute_credit_date(self):
        for li in self:
            if li.invoice_date_due:
                li.credit_date = li.invoice_date_due + relativedelta(days= li.partner_id.payment_term)

class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_last_30_days = fields.Date('Payment last 30 Days')



class SaleOrder(models.Model):
    _inherit = "sale.order"

    allow_credit = fields.Boolean('Allow Over Credit?')
    z_user_id = fields.Many2one('res.users','Technical Representative')
    # state = fields.Selection(selection_add=[
    #     ('draft', 'Quotation'),
    #     ('sent', 'Quotation Sent'),
    #     ('waiting_for_approval','Credit Blocked'),
    #     ('sale', 'Sales Order'),
    #     ('done', 'Locked'),
    #     ('cancel', 'Cancelled'),
    #     ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    z_check_limiit = fields.Boolean('Check Credit Limit')
    z_check_approve = fields.Boolean('Check Credit Limit Approve')
    credit_days = fields.Float('Credit Days')
    credit_limits = fields.Float('Credit Limit')
    sale_amount = fields.Float('Sale Amount 30 Days')
    sale_last_30_days = fields.Date('Sale Last 30 Days')
    payment_last_30 = fields.Float('Payment Last 30 Days')
    last_payment = fields.Float('Last Payment')
    last_payment_date = fields.Date('Last Payment Date')

    next_payment_date = fields.Date('Next Payment Commitment Date')
    next_payment_amt = fields.Float('Next Payment Commitment Amount')

    def action_confirm(self):
        for l in self:
            if not self.state == 'credit':
                if l.z_check_limiit == False:
                    raise ValidationError(_("Check Credit Limit"))
                if l.z_check_approve == True:
                    raise ValidationError(_("This customer has overdue, cannot confirm sale order "))
            # if l.payment_term_id.id:
            #     l.payment_term_id.line_ids.days += l.partner_id.payment_term 
            return super(SaleOrder, self).action_confirm()
    
    def action_approval(self):
        #self.ensure_one()
        self.sale_last_30_days = date.today() - relativedelta(days=30) 
        # b=0
        #due_dte=0
        self.z_check_limiit = True
        partner = self.partner_id
        user_id = self.env['res.users'].search([
            ('partner_id', '=', partner.id)], limit=1)
        if user_id and not user_id.has_group('base.group_portal') or not \
                user_id:

            moveline_obj = self.env['account.move']
            com = moveline_obj.search([('partner_id','=',self.partner_id.id),('type', '=', 'out_invoice'),('amount_residual','>', 0),('invoice_date_due','>',date.today())])
            # a = fields.Date.today()
            acc = moveline_obj.search([('partner_id','=',self.partner_id.id)])
            acc_30 = moveline_obj.search([('partner_id','=',self.partner_id.id),('type','=','out_invoice')])
            for l in acc_30:
                l.credit_last_30_days = date.today() - relativedelta(days=30)
            acc_last_30_days = moveline_obj.search([('partner_id','=',self.partner_id.id),('type','=','out_invoice'),('credit_last_30_days','<',date.today())])


            # b = fields.Date.from_string(a)
            # b += relativedelta(days=com.payment_term)
            # da = moveline_obj.search([('partner_id','=',partner.id)])
            # for l in da:
            #     if l.invoice_date_due:
            #         moveline_obj.due_date = l.invoice_date_due + relativedelta(days= self.partner_id.payment_term)
                    # print(moveline_obj.due_date,'aaaaaaaaaaaaaaaaaaaaaaaaaaaa')
                    # pdb.set_trace()

            # print(moveline_obj.invoice_date_due,'aaaaaaaaaaaaaaaaaaaaaaaaaaa')
            # moveline_obj.due_date = moveline_obj.invoice_date_due
            movelines = moveline_obj.search([('partner_id', '=', partner.id),('type', '=', 'out_invoice'),('amount_residual','!=', 0)])
            movelines_due = moveline_obj.search([('partner_id', '=', partner.id),('type', '=', 'out_invoice'),('amount_residual','>', 0),('credit_date','>',date.today())])
            #pdb.set_trace()
            confirm_sale_order = self.env['sale.order'].search([('partner_id', '=', partner.id),'|',
                ('invoice_status', '=', 'to invoice'),'&',('invoice_status', '=', 'no'),('state','!=','waiting_for_approval')])
            sale_order = self.env['sale.order'].search([('partner_id', '=', partner.id),'|',
                ('invoice_status', '=', 'to invoice'),('invoice_status', '=', 'no'),('sale_last_30_days','<',date.today())])
            payment_date = self.env['account.payment'].search([('partner_id','=',self.partner_id.id)])
            for l in payment_date:
                l.payment_last_30_days = date.today() - relativedelta(days=30)
            payment_last = self.env['account.payment'].search([])
            payment = self.env['account.payment'].search([('partner_id','=',self.partner_id.id),('state','=','posted'),('payment_type','=','inbound'),('payment_last_30_days','<',date.today())])
            due, credit,due_total = 0.0, 0.0 ,0.0
            sale,pay = 0.0,0.0
            amount_total = 0.0
            a,t = 0.0,0.0
            ov = 0.0
            s,n ,l= 0.0,0.0,0.0
            for l in payment_last[:-1]:
                self.last_payment = l.amount
                self.last_payment_date = l.payment_date
            for l in payment:
                pay += l.amount
                self.payment_last_30 = pay
            for tot in acc_last_30_days:
                t += tot.amount_total
                # print(t,'VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV')
            for last_30 in sale_order:
                sale += last_30.amount_total
                self.sale_amount = t + sale
            for l in com:
                a += l.amount_residual
                self.credit_days = a
            # sum of the amount of sale ordes
            for status in confirm_sale_order:
                #print(confirm_sale_order)
                amount_total += status.amount_total
                # print(amount_total,'MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM')
            for r in acc:
                for st in confirm_sale_order:
                    ov += r.amount_residual
                    s += st.amount_total
                    n = ov + s
                    l = self.partner_id.credit_limit - n
                    self.credit_limits = l - self.amount_total
                    # print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
            # sum of the amount of account moves
            for line in movelines:
                due += line.amount_residual
            # sum of the amount of account moves over due
            for due_line in movelines_due:
                due_total += due_line.amount_residual
            if self.partner_id.credit_limit == 0.0:
                self.state = 'credit'
            if self.partner_id.credit_limit != 0:    
                if (amount_total + due ) > self.partner_id.credit_limit:
                    if not self.state == 'credit':
                        self.z_check_approve = True
                        self.state = 'waiting_for_approval'
                        # print(amount_total,due,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')    
                elif (amount_total + due ) < self.partner_id.credit_limit:
                    if not self.state == 'credit':
                        for s in movelines:
                            if s.credit_date > date.today():
                                self.z_check_approve = False
                        # print(amount_total,due,'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
                elif (due_total ) > 0.0:
                    if not self.state == 'credit':
                        for r in movelines:
                            if r.credit_date > date.today():
                                # print(due_total,'cccccccccccccccccccccccccccccccccccccccc')
                                self.z_check_approve = True
                                self.state = 'credit'
                if self.z_check_approve == False:
                    self.state = 'credit'
            for l in movelines:
                if l.credit_date < date.today():
                    self.state = 'waiting_for_approval'
                    self.z_check_approve = True
                    # print(l.credit_date,'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP')
            return True

    def over_credit(self):
        for l in self:
            l.state = 'credit'
           

   

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

    def action_info(self):
        view_id = self.env.ref('partner_credit_limit.sale_credit_limit_coustom_view_form').id
        context = self._context.copy()
        
        query = """SELECT SUM(amount_residual_signed) FROM account_move
                    WHERE type = 'out_invoice' AND partner_id = %s AND invoice_date_due < '%s'
                """%(self.partner_id.id,datetime.now().date())
        self.env.cr.execute(query)
        credit_days = self.env.cr.fetchone()[0]
        if credit_days is None:
            credit_days = 0
        
        # query = """SELECT (SELECT SUM(amount_total) FROM sale_order WHERE partner_id = %s AND state = 'sale' AND invoice_status IN ('no','to_invoice')) +
        #         (SELECT SUM(amount_residual_signed) FROM account_move WHERE partner_id = %s)"""%(self.partner_id.id,self.partner_id.id)
        # self.env.cr.execute(query)
        # credit_limit = self.env.cr.fetchone()[0]
        # print(credit_limit,'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS')
        # if credit_limit is None:
        credit_limit = amt = 0
        partner = self.partner_id
        sale_order = self.env['sale.order'].search([('partner_id', '=', partner.id),('state','=','sale'),'|',
                ('invoice_status', '=', 'to invoice'),('invoice_status', '=', 'no')])
        for l in sale_order:
            amt += l.amount_total
        credit_limit = self.amount_total + self.partner_id.total_due +amt - self.partner_id.credit_limit
        print(self.amount_total,self.partner_id.total_due,amt,self.partner_id.credit_limit,'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS')
        
        query = """SELECT SUM(amount_total) FROM sale_order
                    WHERE partner_id = %s AND date_order > '%s' AND state = 'sale'
                """%(self.partner_id.id, datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)-timedelta(days=30))
        self.env.cr.execute(query)
        sale_amount = self.env.cr.fetchone()[0]
        if sale_amount is None:
            sale_amount = 0

        query = """SELECT amount,payment_date FROM account_payment WHERE state = 'posted' AND partner_id = %s AND payment_date > '%s' ORDER BY payment_date
        """%(self.partner_id.id, datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)-timedelta(days=30))
        self.env.cr.execute(query)
        payments = self.env.cr.fetchall()
        total_pay = sum([payment[0] for payment in payments])
        if payments:
            last_pay = payments[-1][0]
            last_pay_day = payments[-1][1]
            return {
                'name':'Sale Order',
                'view_type':'form',
                'view_mode':'form',
                'views' : [(view_id,'form')],
                'res_model':'credit.info',
                'view_id':view_id,
                'type':'ir.actions.act_window',
                'target':'new',
                'context':{'default_name':self.partner_id.credit_limit,
                'default_additional_credit_days':self.partner_id.payment_term,
                'default_total_outstanding_as_on_date':self.partner_id.total_due,
                'default_over_credit_days':credit_days,
                'default_over_credit_limit':credit_limit,
                'default_next_payment_date':self.next_payment_date,
                'default_next_payment_amt':self.next_payment_amt,
                'default_sale_last':sale_amount,
                'default_collection_last':total_pay,
                'default_last_payment':last_pay,
                'default_last_payment_date':last_pay_day,
                'default_credit_days': self.payment_term_id.id},
            }
        else:
            return {
                'name':'Sale Order',
                'view_type':'form',
                'view_mode':'form',
                'views' : [(view_id,'form')],
                'res_model':'credit.info',
                'view_id':view_id,
                'type':'ir.actions.act_window',
                'target':'new',
                'context':{'default_name':self.partner_id.credit_limit,
                'default_additional_credit_days':self.partner_id.payment_term,
                'default_total_outstanding_as_on_date':self.partner_id.total_due,
                'default_over_credit_days':credit_days,
                'default_over_credit_limit':credit_limit,
                'default_next_payment_date':self.next_payment_date,
                'default_next_payment_amt':self.next_payment_amt,
                'default_sale_last':sale_amount,
                'default_collection_last':total_pay,
                'default_last_payment':0,
                'default_last_payment_date':False,
                'default_credit_days': self.payment_term_id.id},
            }
