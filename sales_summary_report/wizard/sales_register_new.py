# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.



import io
import math
import xlwt
import base64
import datetime
import calendar
from xlwt import easyxf
from datetime import timedelta
from odoo import models, fields, api,_
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError,Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
import pdb
class SalesSummary(models.TransientModel):
    _name = "sales.summary"
    _description = "Sales Summary Report"

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    sales_report = fields.Binary('Sales REPORT')
    file_name = fields.Char('File Name')
    sales_report_printed = fields.Boolean('Sales Report Printed')


    @api.constrains('date_start')
    def _code_constrains(self):
        if self.date_start > self.date_end:
            raise ValidationError(_("'Start Date' must be before 'End Date'"))

    def get_summary(self):
        workbook = xlwt.Workbook()
        amount_tot = 0
        column_heading_style = easyxf('font:height 210;font:bold True;align: horiz center;')
        value_heading_style = easyxf('font:height 210;font:bold True;align: horiz right;')
        worksheet = workbook.add_sheet('Sales Report', cell_overwrite_ok=True)
        right_alignment= easyxf('font:height 200; align: horiz right;')
        center_alignment= easyxf('font:height 200; align: horiz center;')
        current_company_name = self.env.user.company_id.name
        report_heading = " Sales Register From" + ' ' + datetime.strftime(self.date_start, '%d-%m-%Y') + ' '+ 'To' + ' '+datetime.strftime( self.date_end, '%d-%m-%Y')
        worksheet.write_merge(1, 1, 6, 12, report_heading, easyxf('font:height 250;font:bold True;align: horiz center;'))
        worksheet.write_merge(2, 2, 6, 12, current_company_name, easyxf('font:height 250;font:bold True;align: horiz center;'))
        worksheet.write(3, 0, _('SL NO'), column_heading_style)
        worksheet.write(3, 1, _('Invoice No'), column_heading_style) 
        worksheet.write(3, 2, _('Invoice Date'), column_heading_style)
        worksheet.write(3, 3, _('Analytical Account Id'), column_heading_style)
        worksheet.write(3, 4, _('Customer Code'), column_heading_style)
        worksheet.write(3, 5, _('Customer Name'), column_heading_style)
        worksheet.write(3, 6, _('GST No'), column_heading_style)
        worksheet.write(3, 7, _('Customer State'), column_heading_style)
        worksheet.write(3, 8, _('Customer City'), column_heading_style)
        worksheet.write(3, 9, _('Sales Team'), column_heading_style)
        worksheet.write(3, 10, _('Sales Person'), column_heading_style)
        worksheet.write(3, 11, _('Journal'), column_heading_style)
        worksheet.write(3, 12, _('Sale Order No'), column_heading_style)
        worksheet.write(3, 13, _('Sales Order Date'), column_heading_style)
        worksheet.write(3, 14, _('Picking ID'), column_heading_style)
        worksheet.write(3, 15, _('Product Category 1'), column_heading_style)
        worksheet.write(3, 16, _('Product Category 2'), column_heading_style)
        worksheet.write(3, 17, _('Product Category 3'), column_heading_style)
        worksheet.write(3, 18, _('Product Code'), column_heading_style)
        worksheet.write(3, 19, _('Product Name'), column_heading_style)
        worksheet.write(3, 20, _('HSN Code'), column_heading_style)
        worksheet.write(3, 21, _('Lot Number'), column_heading_style)
        worksheet.write(3, 22, _('Uom'), column_heading_style)
        worksheet.write(3, 23, _('Unit Price'), column_heading_style)
        worksheet.write(3, 24, _('Qty Invoiced'), column_heading_style)
        worksheet.write(3, 25, _('Amount Exclusive Tax'), column_heading_style)
        worksheet.write(3, 26, _('CGST Rate %'), column_heading_style)
        worksheet.write(3, 27, _('CGST Amount'), column_heading_style)
        worksheet.write(3, 28, _('SGST Rate %'), column_heading_style)
        worksheet.write(3, 29, _('SGST Amount'), column_heading_style)
        worksheet.write(3, 30, _('IGST Rate %'), column_heading_style)
        worksheet.write(3, 31, _('IGST Amount'), column_heading_style)
        worksheet.write(3, 32, _('Total Tax Amount'), column_heading_style)
        worksheet.write(3, 33, _('Amount Inclusive Tax'), column_heading_style)
        worksheet.write(3, 34, _('Payment State'), column_heading_style)
        
        
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
        worksheet.col(28).width = 4500
        worksheet.row(1).height = 300
        worksheet.row(2).height = 300
        partner_dict = {}
        final_value = {}
        row = 4

        for wizard in self:
            total = 0
            count  = 1
            tot_sgst = tot_cgst = tot_gst = tot_amount = tot_cogs_amount = tot_with_tax_amount = tot_gp_amount =  0.0
            
            for invoice in self.env['account.move'].search([('type','=','out_invoice'),('state','=', 'posted'),('invoice_date','>=',wizard.date_start),('invoice_date','<=',wizard.date_end)]):

                sgst_rate= sgst_amount= cgst_rate= cgst_amount=igst_rate=igst_amount =0.0
                for invoice_line in invoice.invoice_line_ids:
                    # looping the each account move lines
                    if invoice_line.product_id.type != 'service': 
                        sale_order_id = self.env['sale.order'].search([('name','=',invoice.invoice_origin)])

                        if invoice.invoice_origin:
                            sale_id = self.env['sale.order'].search([('name','=',invoice.invoice_origin)])
                            currrent_picking = self.env['stock.picking'].search([('origin','=',invoice.invoice_origin),(['state','=','done'])])
                            if currrent_picking:
                                for each_picking in currrent_picking:
                                    for each_prodcut in each_picking.move_ids_without_package:
                                        move_line_id = self.env['stock.move.line'].search([('move_id','=',each_prodcut.id)])
                                        for each_lot in move_line_id:
                                            if each_prodcut.product_id.id == invoice_line.product_id.id:
                                                for each_line in invoice_line.tax_ids:
                                                    if each_line.tax_group_id.name == 'IGST':
                                                        for each_tax in each_line:
                                                            igst_rate  = each_tax.amount if each_tax.amount else ' '
                                                    elif each_line.tax_group_id.name == 'GST':
                                                        for each_tax in each_line.children_tax_ids:
                                                            sgst_rate  = each_tax.amount if each_tax.amount else ' '
                                                            cgst_rate  = each_tax.amount if each_tax.amount else ' '
                                                sub_total_amount = round(each_lot.qty_done*invoice_line.price_unit,2)
                                                sgst_amount = round(sub_total_amount*sgst_rate/100,2)
                                                cgst_amount = round(sub_total_amount*cgst_rate/100,2)
                                                igst_amount = round(sub_total_amount*igst_rate/100,2)
                                                gst_total = round(sgst_amount+cgst_amount+igst_amount,2)
                                                total_with_tax_amount = round(sub_total_amount+gst_total,2)
                                                worksheet.write(row, 0, count,  center_alignment)
                                                worksheet.write(row, 1, invoice.name)
                                                worksheet.write(row, 2, datetime.strftime(invoice.invoice_date, '%d-%m-%Y'))
                                                worksheet.write(row, 3, invoice.z_analytic_account_id.name, center_alignment)
                                                worksheet.write(row, 4, invoice.partner_id.ref if invoice.partner_id.ref else '')
                                                worksheet.write(row, 5, invoice.partner_id.name)
                                                worksheet.write(row, 6, invoice.partner_id.vat)
                                                worksheet.write(row, 7, invoice.partner_id.state_id.name)
                                                worksheet.write(row, 8, invoice.partner_id.city)
                                                worksheet.write(row, 9, invoice.team_id.name, )
                                                worksheet.write(row, 10, invoice.user_id.name)
                                                worksheet.write(row, 11, invoice.journal_id.name)
                                                worksheet.write(row, 12, each_picking.origin)
                                                worksheet.write(row, 13, datetime.strftime(sale_order_id.date_order, '%d-%m-%Y') if sale_order_id.date_order else '' , center_alignment)
                                                worksheet.write(row, 14, each_picking.name)
                                                path_ids=each_prodcut.product_id.product_tmpl_id.categ_id.parent_path.split('/')
                                                cont_row = 0
                                                col = 15
                                                for path in path_ids:
                                                    if len(path):
                                                        if int(path) and cont_row <= 3:
                                                            categ_ids = self.env['product.category'].search([('id','=',int(path))])
                                                            worksheet.write(row, col, categ_ids.name, center_alignment)
                                                            cont_row += 1
                                                            col += 1
                                                worksheet.write(row, 18, each_prodcut.product_id.default_code, center_alignment)
                                                worksheet.write(row, 19, each_prodcut.product_id.name)
                                                worksheet.write(row, 20, each_prodcut.product_id.l10n_in_hsn_code if each_prodcut.product_id.l10n_in_hsn_code else ' '  , center_alignment)
                                                worksheet.write(row, 21, each_lot.lot_id.name )
                                                worksheet.write(row, 22, each_prodcut.product_uom.name)
                                                worksheet.write(row, 23, invoice_line.price_unit, right_alignment)
                                                worksheet.write(row, 24, each_lot.qty_done, right_alignment)
                                                worksheet.write(row, 25, sub_total_amount, right_alignment)
                                                worksheet.write(row, 26, cgst_rate, right_alignment)
                                                worksheet.write(row, 27, cgst_amount, right_alignment)
                                                worksheet.write(row, 28, sgst_rate, right_alignment)
                                                worksheet.write(row, 29, sgst_amount, right_alignment)
                                                worksheet.write(row, 30, igst_rate, right_alignment)
                                                worksheet.write(row, 31, igst_amount, right_alignment)
                                                worksheet.write(row, 32, gst_total, right_alignment)
                                                worksheet.write(row, 33, total_with_tax_amount, right_alignment)
                                                worksheet.write(row, 34, invoice.invoice_payment_state, )
                                                row += 1
                                                count += 1
                                                # tot_cgst += sgst_amount
                                                # tot_sgst += cgst_amount
                                                # tot_gst += gst_total
                                                # tot_amount += sub_total_amount
                                                 # tot_with_tax_amount += total_with_tax_amount
                            else:
                                po_id = self.env['purchase.order'].search([('origin','=',invoice.invoice_origin)])
                                if po_id:
                                    currrent_picking = self.env['stock.picking'].search([('origin','=',po_id.name),(['state','=','done'])])
                                    for each_picking in currrent_picking:
                                        for each_prodcut in each_picking.move_ids_without_package:
                                                move_line_id = self.env['stock.move.line'].search([('move_id','=',each_prodcut.id)])
                                                for each_lot in move_line_id:
                                                    if each_prodcut.product_id.id == invoice_line.product_id.id:
                                                        for each_line in invoice_line.tax_ids:
                                                            if each_line.tax_group_id.name == 'IGST':
                                                                for each_tax in each_line:
                                                                    igst_rate  = each_tax.amount if each_tax.amount else ' '
                                                            elif each_line.tax_group_id.name == 'GST':
                                                                for each_tax in each_line.children_tax_ids:
                                                                    sgst_rate  = each_tax.amount if each_tax.amount else ' '
                                                                    cgst_rate  = each_tax.amount if each_tax.amount else ' '
                                                        sub_total_amount = round(each_lot.qty_done*invoice_line.price_unit,2)
                                                        sgst_amount = round(sub_total_amount*sgst_rate/100,2)
                                                        cgst_amount = round(sub_total_amount*cgst_rate/100,2)
                                                        igst_amount = round(sub_total_amount*igst_rate/100,2)
                                                        gst_total = round(sgst_amount+cgst_amount+igst_amount,2)
                                                        total_with_tax_amount = round(sub_total_amount+gst_total,2)
                                                        worksheet.write(row, 0, count,  center_alignment)
                                                        worksheet.write(row, 1, invoice.name)
                                                        worksheet.write(row, 2, datetime.strftime(invoice.invoice_date, '%d-%m-%Y'))
                                                        worksheet.write(row, 3, invoice.z_analytic_account_id.name, center_alignment)
                                                        worksheet.write(row, 4, invoice.partner_id.ref if invoice.partner_id.ref else '')
                                                        worksheet.write(row, 5, invoice.partner_id.name)
                                                        worksheet.write(row, 6, invoice.partner_id.vat)
                                                        worksheet.write(row, 7, invoice.partner_id.state_id.name)
                                                        worksheet.write(row, 8, invoice.partner_id.city)
                                                        worksheet.write(row, 9, invoice.team_id.name, )
                                                        worksheet.write(row, 10, invoice.user_id.name)
                                                        worksheet.write(row, 11, invoice.journal_id.name)
                                                        worksheet.write(row, 12, sale_order_id.name)
                                                        worksheet.write(row, 13, datetime.strftime(sale_order_id.date_order, '%d-%m-%Y') if sale_order_id.date_order else '' , center_alignment)
                                                        worksheet.write(row, 14, each_picking.name)
                                                        path_ids=each_prodcut.product_id.product_tmpl_id.categ_id.parent_path.split('/')
                                                        cont_row = 0
                                                        col = 15
                                                        for path in path_ids:
                                                            if len(path):
                                                                if int(path) and cont_row <= 3:
                                                                    categ_ids = self.env['product.category'].search([('id','=',int(path))])
                                                                    worksheet.write(row, col, categ_ids.name, center_alignment)
                                                                    cont_row += 1
                                                                    col += 1
                                                        worksheet.write(row, 18, each_prodcut.product_id.default_code, center_alignment)
                                                        worksheet.write(row, 19, each_prodcut.product_id.name)
                                                        worksheet.write(row, 20, each_prodcut.product_id.l10n_in_hsn_code if each_prodcut.product_id.l10n_in_hsn_code else ' '  , center_alignment)
                                                        worksheet.write(row, 21, each_lot.lot_id.name )
                                                        worksheet.write(row, 22, each_prodcut.product_uom.name)
                                                        worksheet.write(row, 23, invoice_line.price_unit, right_alignment)
                                                        worksheet.write(row, 24, each_lot.qty_done, right_alignment)
                                                        worksheet.write(row, 25, sub_total_amount, right_alignment)
                                                        worksheet.write(row, 26, cgst_rate, right_alignment)
                                                        worksheet.write(row, 27, cgst_amount, right_alignment)
                                                        worksheet.write(row, 28, sgst_rate, right_alignment)
                                                        worksheet.write(row, 29, sgst_amount, right_alignment)
                                                        worksheet.write(row, 30, igst_rate, right_alignment)
                                                        worksheet.write(row, 31, igst_amount, right_alignment)
                                                        worksheet.write(row, 32, gst_total, right_alignment)
                                                        worksheet.write(row, 33, total_with_tax_amount, right_alignment)
                                                        worksheet.write(row, 34, invoice.invoice_payment_state, )
                                                        row += 1
                                                        count += 1
                                                        # tot_cgst += sgst_amount
                                                        # tot_sgst += cgst_amount
                                                        # tot_gst += gst_total
                                                        # tot_amount += sub_total_amount
                                                         # tot_with_tax_amount += total_with_tax_amount

                    else:

                        if invoice.invoice_origin:
                            sale_order_id = self.env['sale.order'].search([('name','=',invoice.invoice_origin)])
                            
                            for each_line in invoice_line.tax_ids:
                                if each_line.tax_group_id.name == 'IGST':
                                    for each_tax in each_line:
                                        igst_rate  = each_tax.amount if each_tax.amount else ' '
                                elif each_line.tax_group_id.name == 'GST':
                                    for each_tax in each_line.children_tax_ids:
                                        sgst_rate  = each_tax.amount if each_tax.amount else ' '
                                        cgst_rate  = each_tax.amount if each_tax.amount else ' '
                            sub_total_amount = round(invoice_line.quantity*invoice_line.price_unit,2)
                            sgst_amount = round(sub_total_amount*sgst_rate/100,2)
                            cgst_amount = round(sub_total_amount*cgst_rate/100,2)
                            igst_amount = round(sub_total_amount*igst_rate/100,2)
                            gst_total = round(sgst_amount+cgst_amount+igst_amount,2)
                            total_with_tax_amount = round(sub_total_amount+gst_total,2)
                            worksheet.write(row, 0, count,  center_alignment)
                            worksheet.write(row, 1, invoice.name)
                            worksheet.write(row, 2, datetime.strftime(invoice.invoice_date, '%d-%m-%Y'))
                            worksheet.write(row, 3, invoice.z_analytic_account_id.name, center_alignment)
                            worksheet.write(row, 4, invoice.partner_id.ref if invoice.partner_id.ref else '')
                            worksheet.write(row, 5, invoice.partner_id.name)
                            worksheet.write(row, 6, invoice.partner_id.vat)
                            worksheet.write(row, 7, invoice.partner_id.state_id.name)
                            worksheet.write(row, 8, invoice.partner_id.city)
                            worksheet.write(row, 9, invoice.team_id.name, )
                            worksheet.write(row, 10, invoice.user_id.name)

                            worksheet.write(row, 11, invoice.journal_id.name)
                            worksheet.write(row, 12, sale_order_id.name)

                            worksheet.write(row, 13, datetime.strftime(sale_order_id.date_order, '%d-%m-%Y') if sale_order_id.date_order else '' , center_alignment)
                            path_ids=invoice_line.product_id.product_tmpl_id.categ_id.parent_path.split('/')
                            cont_row = 0
                            col = 15
                            for path in path_ids:
                                if len(path):
                                    if int(path) and cont_row <= 3:
                                        categ_ids = self.env['product.category'].search([('id','=',int(path))])
                                        worksheet.write(row, col, categ_ids.name, center_alignment)
                                        cont_row += 1
                                        col += 1
                            worksheet.write(row, 18, invoice_line.product_id.default_code, center_alignment)
                            worksheet.write(row, 19, invoice_line.product_id.name)

                            worksheet.write(row, 20, invoice_line.product_id.l10n_in_hsn_code   , center_alignment)
                            worksheet.write(row, 21, each_lot.lot_id.name )
                            worksheet.write(row, 22, invoice_line.product_uom_id.name)

                            worksheet.write(row, 23, invoice_line.price_unit, right_alignment)
                            worksheet.write(row, 24, invoice_line.quantity, right_alignment)
                            worksheet.write(row, 25, sub_total_amount, right_alignment)
                            worksheet.write(row, 26, cgst_rate, right_alignment)
                            worksheet.write(row, 27, cgst_amount, right_alignment)
                            worksheet.write(row, 28, sgst_rate, right_alignment)
                            worksheet.write(row, 29, sgst_amount, right_alignment)
                            worksheet.write(row, 30, igst_rate, right_alignment)
                            worksheet.write(row, 31, igst_amount, right_alignment)
                            worksheet.write(row, 32, gst_total, right_alignment)
                            worksheet.write(row, 33, total_with_tax_amount, right_alignment)
                            worksheet.write(row, 34, invoice.invoice_payment_state, )

                            row += 1
                            count += 1
                # worksheet.write(row, 20, tot_amount, value_heading_style)
                # worksheet.write(row, 24, tot_sgst, value_heading_style)
                # worksheet.write(row, 25, tot_cgst, value_heading_style)
                # worksheet.write(row, 27, tot_gst, value_heading_style)
                # worksheet.write(row, 28, tot_with_tax_amount, value_heading_style)


        fp = io.BytesIO()
        workbook.save(fp)
        excel_file = base64.encodestring(fp.getvalue())
        self.sales_report = excel_file
        self.file_name = 'Sales Register.xls'
        self.sales_report_printed = True
        fp.close()

        return {
        'view_mode': 'form',
        'res_id': self.id,
        'res_model': 'sales.summary',
        'view_type': 'form',
        'type': 'ir.actions.act_window',
        'context': self.env.context,
        'target': 'new',
                   }
