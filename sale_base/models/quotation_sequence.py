from odoo import models, api, fields,_
import pdb
class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    quotation_no = fields.Char(string='Quotation No', required=True, copy=False, readonly=True,
                   index=True, default=lambda self: _('New'))
    copy_quotation_name = fields.Char("Name")

    current_revision_id = fields.Many2one('sale.order','Current revision',readonly=True,copy=True,track_visibility='onchange')
    old_revision_ids = fields.One2many('sale.order','current_revision_id','Old revision',readonly=True,context={'active_test': False},track_visibility='onchange')
    z_order_history_line = fields.One2many('order.history','order_revision_id','Order History',readonly=True,context={'active_test': False},track_visibility='onchange')
    revision_number = fields.Integer('Revision',copy=False)
    unrevisioned_name = fields.Char('Unrevisioned Name',copy=True,readonly=True)
    active = fields.Boolean('Active',default=True,copy=True)  
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
     default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.",track_visibility='onchange')
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'),track_visibility='onchange')
    z_is_cancel= fields.Boolean("Cancelled.") 
 
    #  Overiding the Create function for generating the new Quotation Sequence LIke SQ0001
    @api.model
    def create(self, vals):
        if vals.get('quotation_no', _('New')) == _('New') :
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            if 'company_id' in vals:
                vals['quotation_no'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'sale.quotation', sequence_date=seq_date) or _('New')
            else:
                vals['quotation_no'] = self.env['ir.sequence'].next_by_code('sale.quotation', sequence_date=seq_date) or _('New')
        
        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
        vals['name'] = vals['quotation_no']
        result = super(SaleOrderInherit, self).create(vals)
        return result


    #  Overiding the conform button function for creating the sale Order Sequence Like SO0001
    def action_confirm(self):
        if self.name and self.z_is_cancel != True:
                self.name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code('sale.orders', sequence_date=self.date_order) 
                self.z_is_cancel = True
        else:
            # Find the confirm Sale order for replace the same order number if the user confirm the again and again 
            cancel_ids = self.env['order.history'].search([('order_revision_id','=',self.id)])
            for line in cancel_ids:
                if line.name[0:2] == 'SO':
                    self.name= line.name

        super(SaleOrderInherit, self).action_confirm()
        return True
        
    #  Overindig the draft button function to continue the revision number and Sale Order Number
    def action_draft(self):
        super(SaleOrderInherit, self)
        vals={
                'name':self.name,
                'order_revision_id':self.id,
                }
        self.z_order_history_line = [(0, 0, vals)]
        if self.revision_number == 0:
            self.write({
                'name': self.quotation_no +'-' + str(1),
                'state': 'draft',
                'signature': False,
                'signed_by': False,
                'signed_on': False,
                'revision_number':1,})
        else:
            self.write({
                'name': self.quotation_no +'-' + str(self.revision_number),
                'state': 'draft',
                'signature': False,
                'signed_by': False,
                'signed_on': False,})



    #  Revision Button for Revision Quotation Number. 
    def action_revision(self):
        sale_line = self.mapped('z_order_history_line')
        prev_name = self.name
        revno = self.revision_number+1
        if self.name: 
            self.unrevisioned_name = prev_name
            vals={
                'name':prev_name,
                'order_revision_id':self.id,
                } 
            self.z_order_history_line = [(0, 0, vals)]
            # Updating thr sate ,name and revision number in sale order.
            self.write({
                'state': 'draft',
                'name': self.quotation_no +'-' + str(revno),
                'copy_quotation_name': self.quotation_no +'-' + str(revno),
                'revision_number':revno,
                'active': True,
                'current_revision_id': self.id,
                'unrevisioned_name': self.unrevisioned_name, 
                })

#  Class for shoe the history for the Quotation and Sale orde Numbers
class OrderHostrory(models.Model):
    _name='order.history'
    _description = 'Order History'

    order_revision_id = fields.Many2one('sale.order','Current revision',readonly=True,copy=True)
    name = fields.Char("Order Number")
    