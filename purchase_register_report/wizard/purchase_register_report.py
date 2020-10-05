# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.



from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from datetime import timedelta
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from xlwt import easyxf
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError,Warning
import xlwt
import io
import base64
import datetime
import math
import pdb

class PurchaseRegister(models.TransientModel):
    _name = "purchase.register.report"
    _description = "Purchase Register Report"

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    purchase_report = fields.Binary('Purchase Report')
    file_name = fields.Char('File Name')
    purchase_report_printed = fields.Boolean('Purchase Report Printed')


    @api.constrains('date_start')
    def _code_constrains(self):
        if self.date_start > self.date_end:
            raise ValidationError(_("'Start Date' must be before 'End Date'"))

    def get_summary(self):

        workbook = xlwt.Workbook()
        amount_tot = 0.0
        column_heading_style = easyxf('font:height 210;font:bold True;align: horiz center;')
        value_heading_style = easyxf('font:height 210;font:bold True;align: horiz right;')
        worksheet = workbook.add_sheet('Purchase Register', cell_overwrite_ok=True)
        right_alignment= easyxf('font:height 200; align: horiz right;')
        center_alignment= easyxf('font:height 200; align: horiz center;')
        current_company_name = self.env.user.company_id.name
        # pdb.set_trace()
        # new_date=datetime.datetime.strptime(self.date_start, '%Y-%m-%d')
        # new_date1=datetime.datetime.strptime(self.date_end, '%Y-%m-%d')
        report_heading = " Purchase Register from" + ' ' + datetime.datetime.strftime(self.date_start, '%d-%m-%Y') + ' '+ 'To' + ' '+ datetime.datetime.strftime( self.date_end, '%d-%m-%Y')
        # report_heading = " Purchase Register from" + ' ' + self.date_start +' ' + 'To' + ' ' + self.date_end
        worksheet.write_merge(1, 1, 6, 12, report_heading, easyxf('font:height 250;font:bold True;align: horiz center;'))
        worksheet.write_merge(2, 2, 6, 12, current_company_name, easyxf('font:height 250;font:bold True;align: horiz center;'))
        worksheet.write(3, 0, _('SL NO'), column_heading_style)
        worksheet.write(3, 1, _('Bill Number'), column_heading_style)
        worksheet.write(3, 2, _('Bill Date'), column_heading_style)
        worksheet.write(3, 3, _('Vendor Reference'), column_heading_style)
        worksheet.write(3, 4, _('PO No'), column_heading_style)
        worksheet.write(3, 5, _('PO Date'), column_heading_style)
        worksheet.write(3, 6, _('GRN Ref'), column_heading_style)
        worksheet.write(3, 7, _('Partner Name'), column_heading_style)
        worksheet.write(3, 8, _('Partner State'), column_heading_style)
        worksheet.write(3, 9, _('Partner City'), column_heading_style)
        worksheet.write(3, 10, _('GST No'), column_heading_style)
        worksheet.write(3, 11, _('Analytic Account'), column_heading_style)
        worksheet.write(3, 12, _('Journal'), column_heading_style)
        worksheet.write(3, 13, _('Lot No'), column_heading_style)
        worksheet.write(3, 14, _('HSN Code'), column_heading_style)
        worksheet.write(3, 15, _('Product Name'), column_heading_style)
        worksheet.write(3, 16, _('Product Code'), column_heading_style)
        worksheet.write(3, 17, _('Product Category'), column_heading_style)
        # worksheet.write(3, 17, _('Product Category 3'), column_heading_style)
        worksheet.write(3, 18, _('Uom'), column_heading_style)
        # worksheet.write(3, 17, _('Purchase Qty'), column_heading_style)
        worksheet.write(3, 19, _('Billed Quantity'), column_heading_style)
        worksheet.write(3, 20, _('Received Quantity'), column_heading_style)
        # worksheet.write(3, 19, _('Recevied Qty'), column_heading_style)
        worksheet.write(3, 21, _('Unit Price'), column_heading_style)
        worksheet.write(3, 22, _('Amount Exclusive Tax'), column_heading_style)
        worksheet.write(3, 23, _('CGST Rate %'), column_heading_style)
        worksheet.write(3, 24, _('CGST Amount'), column_heading_style)
        worksheet.write(3, 25, _('SGST Rate %'), column_heading_style)
        worksheet.write(3, 26, _('SGST Amount'), column_heading_style)
        worksheet.write(3, 27, _('IGST Rate %'), column_heading_style)
        worksheet.write(3, 28, _('IGST Amount'), column_heading_style)
        worksheet.write(3, 29, _('TDS Rate %'), column_heading_style)
        worksheet.write(3, 30, _('TDS Amount'), column_heading_style)
        worksheet.write(3, 31, _('Total Tax Amount'), column_heading_style)
        worksheet.write(3, 32, _('Amount Inclusive Tax'), column_heading_style)
        worksheet.write(3, 33, _('Payment State'), column_heading_style)
        # worksheet.write(3, 29, _('Net Landed Cost'), column_heading_style)
        worksheet.col(1).width = 4500
        worksheet.col(2).width = 4500
        worksheet.col(3).width = 4500
        worksheet.col(4).width = 4500
        worksheet.col(5).width = 4500
        worksheet.col(6).width = 4500
        worksheet.col(7).width = 4500
        worksheet.col(8).width = 4500
        worksheet.col(9).width = 4500
        worksheet.col(10).width = 4500
        worksheet.col(11).width = 4500
        worksheet.col(12).width = 4500
        worksheet.col(13).width = 5500
        worksheet.col(28).width = 4500
        worksheet.row(1).height = 300
        worksheet.row(2).height = 300
        partner_dict = {}
        final_value = {}
        row = 4

        for wizard in self:

            total = 0
            count  = 1
            date1 = wizard.date_start 
            tot_sgst = tot_cgst = tot_gst = tot_amount = tot_cogs_amount = tot_with_tax_amount = tot_gp_amount = tot_igst = 0.0
            for invoice in self.env['account.move'].search([('type','=','in_invoice'),('state','in', ['posted']),('invoice_date','>=',wizard.date_start),('invoice_date','<=',wizard.date_end)]):

                sgst_rate= sgst_amount= cgst_rate= cgst_amount= tds_rate=tds_amount=igst_amount =igst_rate=sub_total_amount=gst_total=total_with_tax_amount= 0.0
                p_count=0

                
                picking_list = []
                

                for invoice_line in invoice.invoice_line_ids:
                    #     # if invoice_line.purchase_line_id.order_id:
                    #     # purchase_date=datetime.datetime.strftime(invoice_line.purchase_line_id.order_id.date_order, '%d-%m-%Y')
                    grn_ids = self.env['stock.picking'].search([('state','=','done'),('origin','=',invoice_line.purchase_line_id.order_id.name)])
                    qty_rcvd = 0.0
                    qty_inv = 0.0
                    for each_picking in grn_ids:

                        for grn_line in each_picking.move_ids_without_package:
                            if invoice_line.purchase_line_id.order_id:
                                purchase_date=datetime.datetime.strftime(invoice_line.purchase_line_id.order_id.date_order, '%d-%m-%Y')

                                if grn_line.product_id.id == invoice_line.product_id.id :
                                    # print("iffffffeeeeeeeeeeeeeeeeeeeeeee",invoice.name)
                                    stock_move_line_id = self.env['stock.move.line'].search([('move_id','=',grn_line.id),('product_id','=',grn_line.product_id.id)])
                                    for each_lot in stock_move_line_id:


                                        for each_line in invoice_line.tax_ids:
                                            if each_line.tax_group_id.name == 'IGST':
                                                for each_tax in each_line:
                                                    igst_rate  = each_tax.amount if each_tax.amount else ' '
                                            elif each_line.tax_group_id.name == 'TDS':
                                                for each_tax in each_line:
                                                    tds_rate  = each_tax.amount if each_tax.amount else ' '
                                            elif each_line.tax_group_id.name == 'GST':
                                                for each_tax in each_line.children_tax_ids:
                                                    sgst_rate  = each_tax.amount if each_tax.amount else ' '
                                                    cgst_rate  = each_tax.amount if each_tax.amount else ' '
                                        
                                    #     purchase_order_id = self.env['purchase.order'].search([('name','=',invoice.origin)],limit=1)
                                    #     if purchase_order_id:
                                    #         prchs_date=datetime.datetime.strptime(purchase_order_id.date_order, '%Y-%m-%d %H:%M:%S')

                                    #         purchase_date=datetime.datetime.strftime(prchs_date, '%d-%m-%Y')
                                    #         # qty_rcvd = 0.0
                                    #         # for line in purchase_order_id.order_line:
                                    #         #     if invoice_line.product_id.id == line.product_id.id:
                                    #         #         qty_rcvd = line.qty_received
                                    #         #         qty_inv = line.qty_invoiced
                                    #     else:
                                    #         purchase_date =''
                                    #     grn_names =''

                                        # # pdb.set_trace()
                                        # if purchase_order_id:

                                        #     for line in purchase_order_id.order_line:
                                        #         if invoice_line.product_id.id == line.product_id.id:
                                        #             qty_rcvd = line.qty_received
                                        #             qty_inv = line.qty_invoiced

                                        # if len(picking_list) >=1:
                                        #     for each in picking_list:
                                        #         grn_names  += each.name +','
                                        # landed_produc_cost =0.0
                                        # landed_ref= ' '
                                        # # if landed_list:
                                        # #     for landed in landed_list:
                                        # #         if landed:
                                        # #             current_id = landed[0]['stock_landed_cost_id']
                                        # #             landed_id = self.env['stock.landed.cost'].search([('id','=',current_id)])
                                        # #             if landed_id:
                                        # #                 landed_ref= landed_id.name
                                        # #             for each_prod in landed_id.valuation_adjustment_lines:
                                        # #                 if each_prod.product_id.id == invoice_line.product_id.id:
                                        # #                     landed_produc_cost += each_prod.additional_landed_cost

                                        sub_total_amount = invoice_line.price_unit*invoice_line.quantity
                                        sgst_amount = sub_total_amount*sgst_rate/100
                                        cgst_amount =sub_total_amount*cgst_rate/100
                                        igst_amount =sub_total_amount*igst_rate/100
                                        tds_amount = sub_total_amount*tds_rate/100
                                        gst_total = sgst_amount+cgst_amount+igst_amount
                                        total_with_tax_amount = sub_total_amount + gst_total +tds_amount
                                        # # inv_date1=datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d')

                                        worksheet.write(row, 0, count,  center_alignment)
                                        worksheet.write(row, 1, invoice.name ,center_alignment)
                                        worksheet.write(row, 2, datetime.datetime.strftime(invoice.invoice_date, '%d-%m-%Y'),center_alignment)
                                        worksheet.write(row, 3, invoice.ref if invoice.ref else ' ' , center_alignment)
                                        worksheet.write(row, 4, invoice_line.purchase_line_id.order_id.name, center_alignment)
                                        # pdb.set_trace()
                                        purchase_date =' '
                                        grn_ids =' '

                                        worksheet.write(row, 5, datetime.datetime.strftime(invoice_line.purchase_line_id.order_id.date_order, '%d-%m-%Y'))
                                        worksheet.write(row, 6, each_picking.name, center_alignment)
                                        # worksheet.write(row, 6, bill_date, center_alignment)
                                        worksheet.write(row, 7, invoice.partner_id.name, center_alignment)
                                        worksheet.write(row, 8, invoice.partner_id.state_id.name, center_alignment)
                                        worksheet.write(row, 9, invoice.partner_id.city, center_alignment)
                                        worksheet.write(row, 10, invoice.partner_id.vat, center_alignment)
                                        worksheet.write(row, 11, invoice_line.analytic_account_id.name)
                                        worksheet.write(row, 12, invoice.journal_id.name )
                                        worksheet.write(row, 13, each_lot.lot_id.name if stock_move_line_id else ' ')
                                        worksheet.write(row, 14, invoice_line.product_id.l10n_in_hsn_code if invoice_line.product_id.l10n_in_hsn_code else ' ', center_alignment)
                                        worksheet.write(row, 15, invoice_line.product_id.name , center_alignment)
                                        worksheet.write(row, 16, invoice_line.product_id.default_code , center_alignment)
                                        # worksheet.write(row, 13, qty_rcvd , center_alignment)
                                        # worksheet.write(row, 14, invoice_line.product_id.qty_invoiced , center_alignment)
                                        # _ids= invoice_line.product_id.product_tmpl_id
                                        # cat_name = []
                                        # pdb.set_trace()
                                        # for each_prod in invoice_line.product_id:
                                        #     if each_prod.categ_id.id:
                                        #         cat_name .append(each_prod.categ_id.name)
                                        # print(cat_name)

                                        # if path_ids:
                                        #     cont_row = 0
                                        #     col = 15
                                        #     for path in path_ids.parent_path.split('/'):
                                        #         if len(path):
                                        #             if int(path) and cont_row <= 3:
                                        #                 categ_ids = self.env['product.category'].search([('id','=',int(path))])
                                        #                 cont_row += 1
                                        # col += 1
                                        worksheet.write(row, 17, invoice_line.product_id.categ_id.complete_name, center_alignment)
                                        worksheet.write(row, 18, invoice_line.product_uom_id.name, center_alignment)
                                        # pdb.set_trace()
                                        # worksheet.write(row, 18, each_lot.product_qty,right_alignment)
                                        worksheet.write(row, 19, invoice_line.purchase_line_id.qty_invoiced, center_alignment)
                                        worksheet.write(row, 20, each_lot.qty_done , center_alignment)
                                        # worksheet.write(row, 18, invoice_line.qty_invoiced, right_alignment)
                                        # worksheet.write(row, 19, invoice_line.qty_received, right_alignment)
                                        worksheet.write(row, 21, invoice_line.price_unit, right_alignment)
                                        worksheet.write(row, 22, sub_total_amount, right_alignment)
                                        worksheet.write(row, 23, cgst_rate, right_alignment)
                                        worksheet.write(row, 24, cgst_amount, right_alignment)
                                        worksheet.write(row, 25, sgst_rate, right_alignment)
                                        worksheet.write(row, 26, sgst_amount, right_alignment)
                                        worksheet.write(row, 27, igst_rate, right_alignment)
                                        worksheet.write(row, 28, igst_amount, right_alignment)
                                        worksheet.write(row, 29, tds_rate, right_alignment)
                                        worksheet.write(row, 30, tds_amount, right_alignment)
                                        worksheet.write(row, 31, gst_total, right_alignment)
                                        worksheet.write(row, 32, total_with_tax_amount, right_alignment)
                                        worksheet.write(row, 33, invoice.invoice_payment_state, right_alignment)
                                        # worksheet.write(row, 14, invoice_line.product_id.qty_invoiced , center_alignment)
                                        # worksheet.write(row, 30, landed_produc_cost, right_alignment)
                                        # worksheet.write(row, 32, landed_produc_cost+sub_total_amount, right_alignment)
                                        row += 1
                                        count += 1
                                        p_count += 1
                                elif invoice_line.product_id.type == 'service':
                                    stock_move_line_id = self.env['stock.move.line'].search([('move_id','=',grn_line.id),('product_id','=',grn_line.product_id.id)])
                                    for each_lot in stock_move_line_id:


                                        for each_line in invoice_line.tax_ids:
                                            if each_line.tax_group_id.name == 'IGST':
                                                for each_tax in each_line:
                                                    igst_rate  = each_tax.amount if each_tax.amount else ' '
                                            elif each_line.tax_group_id.name == 'TDS':
                                                for each_tax in each_line:
                                                    tds_rate  = each_tax.amount if each_tax.amount else ' '
                                            elif each_line.tax_group_id.name == 'GST':
                                                for each_tax in each_line.children_tax_ids:
                                                    sgst_rate  = each_tax.amount if each_tax.amount else ' '
                                                    cgst_rate  = each_tax.amount if each_tax.amount else ' '
                                        
                                    #     purchase_order_id = self.env['purchase.order'].search([('name','=',invoice.origin)],limit=1)
                                    #     if purchase_order_id:
                                    #         prchs_date=datetime.datetime.strptime(purchase_order_id.date_order, '%Y-%m-%d %H:%M:%S')

                                    #         purchase_date=datetime.datetime.strftime(prchs_date, '%d-%m-%Y')
                                    #         # qty_rcvd = 0.0
                                    #         # for line in purchase_order_id.order_line:
                                    #         #     if invoice_line.product_id.id == line.product_id.id:
                                    #         #         qty_rcvd = line.qty_received
                                    #         #         qty_inv = line.qty_invoiced
                                    #     else:
                                    #         purchase_date =''
                                    #     grn_names =''

                                        # # pdb.set_trace()
                                        # if purchase_order_id:

                                        #     for line in purchase_order_id.order_line:
                                        #         if invoice_line.product_id.id == line.product_id.id:
                                        #             qty_rcvd = line.qty_received
                                        #             qty_inv = line.qty_invoiced

                                        # if len(picking_list) >=1:
                                        #     for each in picking_list:
                                        #         grn_names  += each.name +','
                                        # landed_produc_cost =0.0
                                        # landed_ref= ' '
                                        # # if landed_list:
                                        # #     for landed in landed_list:
                                        # #         if landed:
                                        # #             current_id = landed[0]['stock_landed_cost_id']
                                        # #             landed_id = self.env['stock.landed.cost'].search([('id','=',current_id)])
                                        # #             if landed_id:
                                        # #                 landed_ref= landed_id.name
                                        # #             for each_prod in landed_id.valuation_adjustment_lines:
                                        # #                 if each_prod.product_id.id == invoice_line.product_id.id:
                                        # #                     landed_produc_cost += each_prod.additional_landed_cost

                                        sub_total_amount = invoice_line.price_unit*invoice_line.quantity
                                        sgst_amount = sub_total_amount*sgst_rate/100
                                        cgst_amount =sub_total_amount*cgst_rate/100
                                        igst_amount =sub_total_amount*igst_rate/100
                                        tds_amount = sub_total_amount*tds_rate/100
                                        gst_total = sgst_amount+cgst_amount+igst_amount
                                        total_with_tax_amount = sub_total_amount + gst_total +tds_amount
                                        # # inv_date1=datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d')

                                        worksheet.write(row, 0, count,  center_alignment)
                                        worksheet.write(row, 1, invoice.name ,center_alignment)
                                        worksheet.write(row, 2, datetime.datetime.strftime(invoice.invoice_date, '%d-%m-%Y'),center_alignment)
                                        worksheet.write(row, 3, invoice.ref if invoice.ref else ' ' , center_alignment)
                                        worksheet.write(row, 4, invoice_line.purchase_line_id.order_id.name, center_alignment)
                                        # pdb.set_trace()
                                        purchase_date =' '
                                        grn_ids =' '

                                        worksheet.write(row, 5, datetime.datetime.strftime(invoice_line.purchase_line_id.order_id.date_order, '%d-%m-%Y'))
                                        worksheet.write(row, 6, each_picking.name, center_alignment)
                                        # worksheet.write(row, 6, bill_date, center_alignment)
                                        worksheet.write(row, 7, invoice.partner_id.name, center_alignment)
                                        worksheet.write(row, 8, invoice.partner_id.state_id.name, center_alignment)
                                        worksheet.write(row, 9, invoice.partner_id.city, center_alignment)
                                        worksheet.write(row, 10, invoice.partner_id.vat, center_alignment)
                                        worksheet.write(row, 11, invoice_line.analytic_account_id.name)
                                        worksheet.write(row, 12, invoice.journal_id.name )
                                        worksheet.write(row, 13,  ' ')
                                        worksheet.write(row, 14, invoice_line.product_id.l10n_in_hsn_code if invoice_line.product_id.l10n_in_hsn_code else ' ', center_alignment)
                                        worksheet.write(row, 15, invoice_line.product_id.name , center_alignment)
                                        # worksheet.write(row, 16, invoice_line.product_id.default_code , center_alignment)
                                        # worksheet.write(row, 13, qty_rcvd , center_alignment)
                                        # worksheet.write(row, 14, invoice_line.product_id.qty_invoiced , center_alignment)
                                        # _ids= invoice_line.product_id.product_tmpl_id
                                        # cat_name = []
                                        # pdb.set_trace()
                                        # for each_prod in invoice_line.product_id:
                                        #     if each_prod.categ_id.id:
                                        #         cat_name .append(each_prod.categ_id.name)
                                        # print(cat_name)

                                        # if path_ids:
                                        #     cont_row = 0
                                        #     col = 15
                                        #     for path in path_ids.parent_path.split('/'):
                                        #         if len(path):
                                        #             if int(path) and cont_row <= 3:
                                        #                 categ_ids = self.env['product.category'].search([('id','=',int(path))])
                                        #                 cont_row += 1
                                        # col += 1
                                        worksheet.write(row, 16, invoice_line.product_id.categ_id.complete_name, center_alignment)
                                        worksheet.write(row, 17, invoice_line.product_uom_id.name, center_alignment)
                                        # pdb.set_trace()
                                        # worksheet.write(row, 18, each_lot.product_qty,right_alignment)
                                        worksheet.write(row, 19, invoice_line.quantity, center_alignment)
                                        worksheet.write(row, 20, invoice_line.quantity , center_alignment)
                                        # worksheet.write(row, 18, invoice_line.qty_invoiced, right_alignment)
                                        # worksheet.write(row, 19, invoice_line.qty_received, right_alignment)
                                        worksheet.write(row, 21, invoice_line.price_unit, right_alignment)
                                        worksheet.write(row, 22, sub_total_amount, right_alignment)
                                        worksheet.write(row, 23, cgst_rate, right_alignment)
                                        worksheet.write(row, 24, cgst_amount, right_alignment)
                                        worksheet.write(row, 25, sgst_rate, right_alignment)
                                        worksheet.write(row, 26, sgst_amount, right_alignment)
                                        worksheet.write(row, 27, igst_rate, right_alignment)
                                        worksheet.write(row, 28, igst_amount, right_alignment)
                                        worksheet.write(row, 29, tds_rate, right_alignment)
                                        worksheet.write(row, 30, tds_amount, right_alignment)
                                        worksheet.write(row, 31, gst_total, right_alignment)
                                        worksheet.write(row, 32, total_with_tax_amount, right_alignment)
                                        worksheet.write(row, 33, invoice.invoice_payment_state, right_alignment)
                                        # worksheet.write(row, 14, invoice_line.product_id.qty_invoiced , center_alignment)
                                        # worksheet.write(row, 30, landed_produc_cost, right_alignment)
                                        # worksheet.write(row, 32, landed_produc_cost+sub_total_amount, right_alignment)
                                        row += 1
                                        count += 1
                                        p_count += 1            
                    else:
                        # for each_picking in grn_ids:
                        #     # pdb.set_trace()
                        #     for grn_line in each_picking.move_ids_without_package:
                        # print("Elseeeeeeeeeeeeeeeeeeeeeee",invoice.name)
                        if not invoice.invoice_origin:
                            worksheet.write(row, 0, count,  center_alignment)
                            worksheet.write(row, 1, invoice.name ,center_alignment)
                            worksheet.write(row, 2, datetime.datetime.strftime(invoice.invoice_date, '%d-%m-%Y'),center_alignment)
                            worksheet.write(row, 3, invoice.ref if invoice.ref else ' ' , center_alignment)
                            purchase_date =' '
                            grn_ids =' '
                            for each_line in invoice_line.tax_ids:
                                if each_line.tax_group_id.name == 'IGST':
                                    for each_tax in each_line:
                                        igst_rate  = each_tax.amount if each_tax.amount else ' '
                                elif each_line.tax_group_id.name == 'TDS':
                                                    for each_tax in each_line:
                                                        tds_rate  = each_tax.amount if each_tax.amount else ' '
                                elif each_line.tax_group_id.name == 'GST':
                                    for each_tax in each_line.children_tax_ids:
                                        sgst_rate  = each_tax.amount if each_tax.amount else ' '
                                        cgst_rate  = each_tax.amount if each_tax.amount else ' '
                            stock_move_line_id = self.env['stock.move.line'].search([('move_id','=',grn_line.id),('product_id','=',grn_line.product_id.id)])
                            sub_total_amount = invoice_line.price_unit*invoice_line.quantity
                            sgst_amount = sub_total_amount*sgst_rate/100
                            cgst_amount = sub_total_amount*cgst_rate/100
                            igst_amount = sub_total_amount*igst_rate/100
                            tds_amount = sub_total_amount*igst_rate/100
                            gst_total = sgst_amount+cgst_amount+igst_amount
                            total_with_tax_amount = sub_total_amount + gst_total+tds_amount

                            # worksheet.write(row, 5, datetime.datetime.strftime(invoice_line.purchase_line_id.order_id.date_order, '%d-%m-%Y'))
                            # worksheet.write(row, 6, each_picking.name, center_alignment)
                            # worksheet.write(row, 6, bill_date, center_alignment)
                            worksheet.write(row, 7, invoice.partner_id.name, center_alignment)
                            worksheet.write(row, 8, invoice.partner_id.state_id.name, center_alignment)
                            worksheet.write(row, 9, invoice.partner_id.city, center_alignment)
                            worksheet.write(row, 10, invoice.partner_id.vat, center_alignment)
                            worksheet.write(row, 11, invoice_line.analytic_account_id.name)
                            worksheet.write(row, 12, invoice.journal_id.name )
                            worksheet.write(row, 13, ' ', center_alignment)
                            worksheet.write(row, 14, invoice_line.product_id.l10n_in_hsn_code if invoice_line.product_id.l10n_in_hsn_code else ' ', center_alignment)
                            worksheet.write(row, 15, invoice_line.product_id.name , center_alignment)
                            worksheet.write(row, 16, invoice_line.product_id.default_code , center_alignment)
                            worksheet.write(row, 17, invoice_line.product_id.categ_id.complete_name, center_alignment)
                            worksheet.write(row, 18, invoice_line.product_uom_id.name, center_alignment)
                            worksheet.write(row, 19, invoice_line.quantity, right_alignment)
                            worksheet.write(row, 20, invoice_line.quantity, center_alignment)
                            # worksheet.write(row, 21, invoice_line.quantity , center_alignment)
                            # worksheet.write(row, 18, invoice_line.qty_invoiced, right_alignment)
                            # worksheet.write(row, 19, invoice_line.qty_received, right_alignment)
                            worksheet.write(row, 21, invoice_line.price_unit, right_alignment)
                            worksheet.write(row, 22, sub_total_amount, right_alignment)
                            worksheet.write(row, 23, cgst_rate, right_alignment)
                            worksheet.write(row, 24, cgst_amount, right_alignment)
                            worksheet.write(row, 25, sgst_rate, right_alignment)
                            worksheet.write(row, 26, sgst_amount, right_alignment)
                            worksheet.write(row, 27, igst_rate, right_alignment)
                            worksheet.write(row, 28, igst_amount, right_alignment)
                            worksheet.write(row, 29, tds_rate, right_alignment)
                            worksheet.write(row, 30, tds_amount, right_alignment)
                            worksheet.write(row, 31, gst_total, right_alignment)
                            worksheet.write(row, 32, total_with_tax_amount, right_alignment)
                            worksheet.write(row, 33, invoice.invoice_payment_state, right_alignment)
                            row += 1
                            count += 1
                            p_count += 1
                                # tot_cgst += sgst_amount
                                # tot_sgst += cgst_amount
                                # # tot_igst += igst_amount
                                # # tot_gst += gst_total
                                # tot_amount += sub_total_amount
                                # tot_with_tax_amount += total_with_tax_amount
                        # worksheet.write(row, 19, tot_amount, value_heading_style)
                        # worksheet.write(row, 23, tot_sgst, value_heading_style)
                        # worksheet.write(row, 24, tot_cgst, value_heading_style)
                        # worksheet.write(row, 25, tot_igst, value_heading_style)
                        # worksheet.write(row, 26, tot_gst, value_heading_style)
                        # worksheet.write(row, 27, tot_with_tax_amount, value_heading_style)


        fp = io.BytesIO()
        workbook.save(fp)
        excel_file = base64.encodestring(fp.getvalue())
        self.purchase_report = excel_file
        self.file_name = 'Purchase Register.xls'
        self.purchase_report_printed = True
        fp.close()

        return {
        'view_mode': 'form',
        'res_id': self.id,
        'res_model': 'purchase.register.report',
        'view_type': 'form',
        'type': 'ir.actions.act_window',
        'context': self.env.context,
        'target': 'new',
                   }