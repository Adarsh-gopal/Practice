# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import pdb
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from datetime import datetime, timedelta,date


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    scheduled_dispatch_date = fields.Datetime()

# class Partner(models.Model):
#     _inherit = 'purchase.order'

#     scheduled_dispatch_date = fields.Datetime()


class AccountPayment(models.Model):
    _inherit= 'account.payment'

    cheque_number = fields.Char(string='Cheque Number')
    cheque_date = fields.Date(string='Cheque Date')
    customer_vendor_bank_name = fields.Char(string='Customer / Vendor Bank Name')
    payer_payee = fields.Char(string='Payer / Payee')

class PaymentCustom(models.Model):
    _name = 'payment.custom'
    _description = 'payment custom'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment = fields.Many2one('payment.custom',string='Payment Method')
    transporter = fields.Many2one('res.partner',string='Transporter',domain="[('transport_vendor', '=', 'True')]")
    customer_order_date = fields.Date(string='Customer Order Date')
    customer_order_number = fields.Char(string='Customer Order Number')

    @api.onchange('partner_id')
    def  Onchange_transporter(self):
        for l in self:
            l.transporter = l.partner_id.preffered_transporter
            l.z_user_id = l.partner_id.z_user_id.id
            l.payment = l.partner_id.z_payment_custom.id
            l.incoterm = l.partner_id.incoterms


class AccountMove(models.Model):
    _inherit= 'account.move'

    destination = fields.Char(string='Destination')
    vehicle_number = fields.Char(string='Vehicle Number')
    eway_bill_number = fields.Char(string='E-Way Bill Number')
    lr_way_bill_number = fields.Char(string='LR-Way Bill Number')
    lr_way_bill_date = fields.Date(string='LR-Way Bill Date')
    customer_order_date = fields.Date(string='Customer Order Date')
    customer_order_number = fields.Char(string='Customer Order Number')
    payment = fields.Many2one('payment.custom',string='Payment Method',store=True,readonly=False,compute='custom_payment')
    transporter = fields.Many2one('res.partner',string='Transporter',store=True,compute='custom_transport',readonly=False,domain="[('transport_vendor', '=', 'True')]")
    #Added by Lokes at 17-06-2020
    despatch_by = fields.Char()
    despatch_through = fields.Char()
    ex_godown = fields.Char()


    @api.depends('partner_id')
    def custom_payment(self):
        for l in self:
            var = self.env['sale.order'].search([('name','=',l.invoice_origin)])
            for line in var:
                l.payment = line.payment.id
                l.customer_order_date = line.customer_order_date
                l.customer_order_number = line.customer_order_number

    @api.depends('partner_id')
    def custom_transport(self):
        for l in self:
            var = self.env['sale.order'].search([('name','=',l.invoice_origin)])
            for line in var:
                l.transporter = line.transporter.id

    

    #Added by Lokes at 17-06-2020
    @api.onchange('invoice_line_ids')
    def _compute_all(self):
        for rec in self:
            if rec.invoice_line_ids:
                rec.despatch_by = rec.invoice_line_ids[0].purchase_line_id.order_id.despatch_by
                rec.despatch_through = rec.invoice_line_ids[0].purchase_line_id.order_id.despatch_through
                rec.ex_godown = rec.invoice_line_ids[0].purchase_line_id.order_id.ex_godown
                
            else:
                rec.despatch_by = rec.despatch_by
                rec.despatch_through = rec.despatch_through
                rec.ex_godown = rec.ex_godown


class ResPartner(models.Model):
    _inherit = "res.partner"

    z_user_id = fields.Many2one('res.users',string='Technical Representative')
    z_payment_custom = fields.Many2one('payment.custom',string='Payment Method')
    # added fileds 
    cin_number = fields.Char(string='CIN Number')
    registraion_date = fields.Char(string='Registration / Incorporation Date ')
    iec_number = fields.Char(string='IEC Number')
    tan_number = fields.Char(string='TAN Number')
    msme_adhar_number = fields.Char(string='MSME Aadhar Number')
    customer_rating = fields.Char(string='Customer Rating')
    business_plan = fields.Char(string='Business Plan')
    incoterms = fields.Many2one('account.incoterms',string='Incoterms')



class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    package_ids = fields.Many2one('product.packaging',string='Package',store=True,track_visibility='always',compute='compute_pakages_line')
    no_bags = fields.Float(string='No of Bags',store=True,track_visibility='always',compute='compute_pakages')

    @api.depends('product_id')
    def compute_pakages_line(self):
        for l in self:
            rec = self.env['product.packaging'].search([('product_id','=',l.product_id.id)])
            for r in rec:
                l.package_ids = r.id
               

    @api.depends('qty_done')
    def compute_pakages(self):
        for l in self:
            if l.package_ids:
                if l.package_ids.qty > 0.0:
                    if l.qty_done > 0.0:
                        l.no_bags = l.qty_done/l.package_ids.qty
                    else:
                        l.no_bags = False
                else:
                    l.no_bags = False
            else:
                l.no_bags = False



class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    z_steping_id = fields.One2many('step.discription','z_steping')

class MrpStep(models.Model):
    _name = 'step.discription'
    _description='Step Discription'

    z_steping = fields.Many2one('mrp.routing.workcenter')
    discription = fields.Char(string='Description')

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    temp_id = fields.One2many('temp.description','z_temp_id')
    ref = fields.Char(string='Internal Reference',store=True,compute='compute_lot')

    @api.depends('finished_lot_id')
    def compute_lot(self):
        for l in self:
            l.ref = l.production_id.internal_reference


   
class MrpTemprature(models.Model):
    _name = 'temp.description'
    _description = 'Temp Description'

    z_temp_id = fields.Many2one('mrp.workorder')
    description = fields.Char(string='Description')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    temp = fields.Float(string='Temprature (in Degrees Celcius)') 
    ph = fields.Float(string='pH')
    volumn = fields.Float(string='Volume (in Cubic meters)')

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_plan(self):
        rec = super(MrpProduction,self).button_plan()
        for l in self:
            for s in l.routing_id.operation_ids:
                sas = self.env['mrp.workorder'].search([('production_id','=',l.id),('operation_id','=',s.id)])
                for r in sas:
                    var = self.env['mrp.routing.workcenter'].search([('id','=',r.operation_id.id)])
                    for d in var:
                        for m in d.z_steping_id:
                            self.env['temp.description'].create({
                                'description':m.discription,
                                'z_temp_id':r.id,
                                })
        return rec

#Added by Lokesh at 17-06-2020
class PurchesOrder(models.Model):
    _inherit='purchase.order'
    despatch_by = fields.Char()
    despatch_through = fields.Char()
    ex_godown = fields.Char() 
    property_payment_term_id = fields.Many2one('payment.custom')
    incoterm_id = fields.Many2one('account.incoterms', string="Incoterms", store=True)
    
#Added by Nikitha at 13-07-2020
    @api.onchange('partner_id')
    def Onchange_incoterm(self):
        for rec in self:
            if rec.partner_id.incoterms:
                rec.incoterm_id = rec.partner_id.incoterms.id
            else:
                rec.incoterm_id = None

    @api.onchange('partner_id')
    def Onchange_payment(self):
        for rec in self:
            if rec.partner_id.z_payment_custom:
                rec.property_payment_term_id =rec.partner_id.z_payment_custom
            else:
                property_payment_term_id = None


    
#Added by shashank on 30-06-2020
class ProductMaster(models.Model):
    _inherit = 'product.template'

    chemical_name = fields.Char(string='Chemical Name')
    cas = fields.Char(string='CAS #')
    sds = fields.Selection([('yes', 'Yes'), ('no', 'No'),('na','Na')], string='Cas')
    hazard_class = fields.Char(string='Hazard Class')
    risk_phrases = fields.Char(string='Risk Phrases')
    safety_phrases = fields.Char(string='Safety Phrases')
    zdhc_approved = fields.Selection([('yes', 'Yes'), ('no', 'No')],string='ZDHC Approved')
    gots_approved = fields.Selection([('yes', 'Yes'), ('no', 'No')],string='GOTS Approved ')
    shel_life = fields.Char(string='Shelf Life')

class Crmteam(models.Model):
    _inherit = 'crm.team'

    member_ids = fields.Many2many(
        'res.users', 'maintenance_team_users_rel', string="Team Members",
        domain=False)





                                

