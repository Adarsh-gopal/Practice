# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = _inherit

    z_partner_category = fields.Many2one('partner.category',string="Partner Category",domain="[('active_id', '=', True)]")
    z_partner = fields.Boolean('Partner')
    customer = fields.Boolean('Customer')
    vendor = fields.Boolean('Vendor')
    transport_vendor= fields.Boolean('Transport Vendor')
    distributor = fields.Boolean('Distributor')
    invoice_vendor = fields.Boolean('Invoice Vendor',store=True,compute='compute_vendor')
    invoice_customer = fields.Boolean('Invoice Customer',store=True,compute='compute_customer')
    invoice_filter = fields.Char('Invoice Filter',store=True,compute='compute_filter')
    preffered_transporter = fields.Many2one('res.partner',string="Preffered Transporter",domain="[('transport_vendor', '=', 'True')]")
    customer_business_type = fields.Many2one('customer.business.type',store=True,string='Customer Business Type')


    @api.model
    def create(self, vals):
        if 'z_partner' in vals and vals['z_partner']:
            sequence_type =  vals.get('z_partner_category')
            sequence_type = self.env['partner.category'].browse(sequence_type)
            if sequence_type:
                vals['ref'] = sequence_type.partner_category.next_by_id()

        return super(ResPartner, self).create(vals)

    @api.onchange('z_partner_category')
    def Onchange_partner(self):
        for l in self:
            if l.z_partner_category.partner_category:
                l.z_partner = True
            else:
                l.z_partner = False

    @api.depends('customer','distributor')
    def compute_customer(self):
        for l in self:
            if l.customer == True or l.distributor == True:
                l.invoice_customer = True
            elif l.customer == True and l.distributor == True:
                l.invoice_customer = True
            elif l.customer == False and l.distributor == False:
                l.invoice_customer = False

    @api.depends('vendor','transport_vendor')
    def compute_vendor(self):
        for l in self:
            if l.vendor == True or l.transport_vendor == True:
                l.invoice_vendor = True
            elif l.vendor == True and l.transport_vendor == True:
                l.invoice_vendor = True
            elif l.vendor == False and l.transport_vendor == False:
                l.invoice_vendor = False

    @api.depends('invoice_customer','invoice_vendor')
    def compute_filter(self):
        for l in self:
            if l.invoice_customer == True:
                l.invoice_filter = 'sale'
            if l.invoice_vendor == True:
                l.invoice_filter = 'purchase'


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name = _inherit

    z_partner = fields.Boolean('Partner')
    default_code= fields.Char(string='Internal Reference',compute = "_trackcode",store=True,readonly=True)
    default_code1= fields.Char(string='Internal Reference code')


    @api.onchange('categ_id')
    def Onchange_partner(self):
        for l in self:
            if l.categ_id.sequence_id:
                l.z_partner = True
            else:
                l.z_partner = False

    @api.depends('default_code1')
    def _trackcode(self):
        for l in self:
            l.default_code = l.default_code1   

    @api.model
    def create(self, vals):
        if 'z_partner' in vals and vals['z_partner']:
            sequence_type =  vals.get('categ_id')
            sequence_type = self.env['product.category'].browse(sequence_type)
            if sequence_type:
                new_code = sequence_type.sequence_id.next_by_id()
                vals.update({'default_code1': new_code,'default_code': new_code})

        return super(ProductTemplate, self).create(vals)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    sequence_id = fields.Many2one('ir.sequence',string='Sequence')


class PartnerCategory(models.Model):
    _name = 'partner.category'
    _description = 'partner category'
    _parent_name = "zparent"
    _parent_store = True
    _rec_name = 'full_name'
    _order = 'full_name'

    name = fields.Char(string='Name',index=True)
    full_name = fields.Char(string='Category Name',store=True,compute='_compute_complete_name')
    zparent = fields.Many2one('partner.category',string='Parent')
    active_id = fields.Boolean(string='Release')
    partner_category = fields.Many2one('ir.sequence',string="Sequence")
    parent_path = fields.Char(index=True)

    @api.depends('name', 'zparent.name')
    def _compute_complete_name(self):
        for location in self:
            if location.zparent:
                location.full_name = '%s / %s' % (location.zparent.full_name, location.name)
            else:
                location.full_name = location.name

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_reference = fields.Char('Partner Category')
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('customer','=',True),('distributor','=',True)]",)

    @api.onchange('partner_id')
    def Onchange_partner(self):
        for l in self:
            l.partner_reference = l.partner_id.z_partner_category.full_name

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    partner_reference = fields.Char('Partner Category')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=False, states=READONLY_STATES, change_default=True, tracking=True, domain="['|', ('vendor', '=', True),('transport_vendor', '=', True)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")

    @api.onchange('partner_id')
    def Onchange_partnerr(self):
        for l in self:
            l.partner_reference = l.partner_id.z_partner_category.name

# class Lead(models.Model):
#     _inherit = "crm.lead"

#     partner_id = fields.Many2one('res.partner', string='Customer', tracking=10, index=True,
#         domain="['|',('customer','=',True),('distributor','=',True)]", help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")

class AccountInvoice(models.Model):
    _inherit = "account.move"

    partner_reference = fields.Char('Partner Category',store=True,track_visibility='always',compute='change_partners')
    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
        states={'draft': [('readonly', False)]},
        domain="[('invoice_filter', '=', invoice_filter_type_domain)]",
        string='Partner', change_default=True)


    @api.depends('partner_id')
    def change_partners(self):
        for l in self:
            l.partner_reference = l.partner_id.z_partner_category.name

class CustomerBusinessType(models.Model):
    _name = 'customer.business.type'

    name = fields.Char(string='Name',store=True)


# class account_payment(models.Model):
#     _inherit = "account.payment"

#     partner_id = fields.Many2one('res.partner', string='Partner', tracking=True, readonly=True, states={'draft': [('readonly', False)]}, domain="['|', ('partner_type','=', 'customer'), ('partner_type', '=','supplier')]")