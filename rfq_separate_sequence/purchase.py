# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
import pdb

class purchase_order(models.Model):
    _inherit = "purchase.order"
    
    rfq_name = fields.Char('Rfq Reference', select=True, copy=False,
                            help="Unique number of the purchase order, "
                                 "computed automatically when the purchase order is created.")
    interchanging_rfq_sequence = fields.Char('Sequence')
    interchanging_po_sequence = fields.Char('Sequence')
    quotation_no = fields.Char(string='Quotation No', required=True, copy=False, readonly=True,
                   index=True, default=lambda self: _('New'))
    copy_quotation_name = fields.Char("Name")

    current_revision_id = fields.Many2one('purchase.order','Current revision',readonly=True,copy=True,track_visibility='onchange')
    old_revision_ids = fields.One2many('purchase.order','current_revision_id','Old revisions',readonly=True,context={'active_test': False},track_visibility='onchange')
    z_order_history_line = fields.One2many('order.historys','order_revision_id','Old revisions',readonly=True,context={'active_test': False},track_visibility='onchange')
    revision_number = fields.Integer('Revision',copy=False,store=True)
    unrevisioned_name = fields.Char('Order Reference',copy=True,readonly=True)
    active = fields.Boolean('Active',default=True,copy=True)  
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
     default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.",track_visibility='onchange')
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'),track_visibility='onchange')
    z_is_cancel= fields.Boolean("Cancelled.")
                
    @api.model
    def create(self, vals):
        if vals.get('quotation_no','New') == 'New':
            vals['quotation_no'] = self.env['ir.sequence'].next_by_code('purchase.order.quot') or 'New'
            vals['rfq_name'] = vals['name'] = vals['quotation_no']
            
        return super(purchase_order, self).create(vals)
        
    def button_confirm(self):
        #res =  super(purchase_order, self).button_confirm()
        for order in self:
            if order.interchanging_rfq_sequence:
                order.write({'name': order.interchanging_po_sequence})
            else:
                new_name = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
                order.write({'interchanging_rfq_sequence':order.name})
                order.write({'name': new_name})
            self.picking_ids.write({'origin': order.interchanging_po_sequence})
            if self.picking_ids:
                for pick in self.picking_ids:
                    pick.move_lines.write({'origin': order.interchanging_po_sequence})
        # if self.name and self.z_is_cancel != True:
        #     self.name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code('purchase.order', sequence_date=self.date_order) 
        #     self.z_is_cancel = True
        # else:
        #     # Find the confirm Sale order for replace the same order number if the user confirm the again and again 
        #     cancel_ids = self.env['order.historys'].search([('order_revision_id','=',self.id)])
        #     for line in cancel_ids:
        #         if line.name[0:1] == 'p':
        #             self.name= line.name
 
        return super(purchase_order, self).button_confirm()
    
    def button_draft(self):
        res = super(purchase_order, self).button_draft()
        if self.interchanging_rfq_sequence:
            self.write({'interchanging_po_sequence':self.name})
            self.write({'name':self.interchanging_rfq_sequence})
        
        return res

    def button_revision(self):
        sale_line = self.mapped('z_order_history_line')
        prev_name = self.name
        revno = self.revision_number+1
        # pdb.set_trace()
        #print("###################",revno)
        if self.name:
            self.unrevisioned_name = prev_name
            vals={
                'name':prev_name,
                'order_revision_id':self.id,
                } 
            self.z_order_history_line = [(0, 0, vals)]
            self.write({
                'state': 'draft',
                'name': self.quotation_no +'-' + str(revno),
                'revision_number': revno,
                'active': True,
                'current_revision_id': self.id,
                'unrevisioned_name': self.unrevisioned_name,
                })

class OrderHostrory(models.Model):
    _name='order.historys'

    order_revision_id = fields.Many2one('purchase.order','Current revision',readonly=True,copy=True)
    name = fields.Char("Order Number")

