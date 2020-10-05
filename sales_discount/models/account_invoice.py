from itertools import groupby
from odoo import api, fields, models, exceptions,_
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.addons import decimal_precision as dp
from odoo.tools.misc import formatLang, format_date, get_lang

class AccountInvoice(models.Model):
	_inherit="account.move"


	#invoice_lines = fields.Char(string="Required Field for sale order category discount")

	#establishing relationship with account discount line to display the page.
	invoice_dis_line_ids = fields.One2many('account.discount.line', 'invoice_categ_dis_id', string='Discount Lines', copy=True, auto_join=True)
	#this field is used to display the sum total of trade discounts used in invoice line similar to tax calculation & is invisible in form
	trade_discount_line_ids = fields.One2many('account.invoice.trade.discount', 'invoice_trade_discount_id',store=True,track_visibility='always',compute="_trade_discount_cal", string='Trade Discount Lines',
        readonly=True, states={'draft': [('readonly', False)]}, copy=True)
	#this field is used to display the sum total of quantity discounts used in invoice line similar to tax calculation & is invisible in form
	quantity_discount_line_ids = fields.One2many('account.invoice.quantity.discount', 'invoice_quantity_discount_id',store=True,track_visibility='always', string='Quantity Discount Lines',
        readonly=True, states={'draft': [('readonly', False)]}, copy=True,compute="_quantity_discount_cal",)
	#this field is used to display the sum total of special discounts used in invoice line similar to tax calculation & is invisible in form
	special_discount_line_ids = fields.One2many('account.invoice.special.discount', 'invoice_special_discount_id',store=True,track_visibility='always', string='Special Discount Lines',
        readonly=True, states={'draft': [('readonly', False)]}, copy=True,compute="_special_discount_cal")
	#this field contains the overall discount values of trade,quantity,special per order
	amount_dis = fields.Monetary(string='Amount Prod Dis', store=True, readonly=True, compute='_total_amount_invoice_discounts')
	#this field contains the overall trade discount values per order
	trade_dis = fields.Monetary(string='Trade Discount', store=True, readonly=True, compute='_total_amount_invoice_discounts')
	#this field contains the overall quantity discount values per order
	quantity_dis = fields.Monetary(string='Quantity Discount', store=True, readonly=True, compute='_total_amount_invoice_discounts')
	#this field contains the overall special discount values per order
	special_dis = fields.Monetary(string='Special Discount', store=True, readonly=True, compute='_total_amount_invoice_discounts')
	check_button = fields.Boolean('Check',store=True)

	# amount_tax = fields.Monetary(string='Total Tax',
 #        store=True, readonly=True)

	
	#renamed the string from standard
	amount_untaxed = fields.Monetary(string='Sales TTO',
        store=True, readonly=True, track_visibility='always',compute='_compute_amount')
	amount_total = fields.Monetary(string='Gross Total',
        store=True, readonly=True,compute='_compute_amount')
	#displaying the total amount without deducting the discount and taxes
	gross_sales = fields.Monetary(string='Gross Sales', store=True, readonly=True,track_visibility='always',compute='_compute_amount') 
	#field to apply visibility conditions to fields in form
	cal_done = fields.Boolean(string="Calculation Done",default=True)
	display_button = fields.Boolean(string="Display Button",store=True,track_visibility='always',compute='compute_display_button')

	# z_fiscal_bool = fields.Boolean(string="Fiscal Value Filter",store=True,compute="func_fiscal_position")

	@api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
	def _compute_amount(self):
		invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
		self.env['account.payment'].flush(['state'])
		if invoice_ids:
			self._cr.execute(
				'''
					SELECT move.id
					FROM account_move move
					JOIN account_move_line line ON line.move_id = move.id
					JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
					JOIN account_move_line rec_line ON
						(rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
						OR
						(rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
					JOIN account_payment payment ON payment.id = rec_line.payment_id
					JOIN account_journal journal ON journal.id = rec_line.journal_id
					WHERE payment.state IN ('posted', 'sent')
					AND journal.post_at = 'bank_rec'
					AND move.id IN %s
				''', [tuple(invoice_ids)]
			)
			in_payment_set = set(res[0] for res in self._cr.fetchall())
		else:
			in_payment_set = {}

		for move in self:
			move.gross_sales = sum(line.gross_total for line in move.invoice_line_ids)
			round_curr = move.currency_id.round
			amount_untaxed = amount_tax = amount_dis = gross_sales = 0.0
			amount_trade = amount_qty = amount_spcl = 0.0
			amt = 0.0
			var = 0.0
			for line in move.invoice_line_ids:
				amount_trade += line.trade_amount
				amount_qty += line.quantity_amount
				amount_spcl += line.special_amount
			total_untaxed = 0.0
			total_untaxed_currency = 0.0
			total_tax = 0.0
			total_tax_currency = 0.0
			total_residual = 0.0
			total_residual_currency = 0.0
			total = 0.0
			total_currency = 0.0
			currencies = set()

			for line in move.line_ids:
				if line.currency_id:
					currencies.add(line.currency_id)

				if move.is_invoice(include_receipts=True):
					# === Invoices ===
					if not line.exclude_from_invoice_tab:
						# Untaxed amount.
						total_untaxed += line.balance
						total_untaxed_currency += line.amount_currency
						total += line.balance
						total_currency += line.amount_currency
						# print(total_untaxed,total_untaxed_currency,total,total_currency,'GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG')
					elif line.tax_line_id:
						# Tax amount.
						total_tax += line.balance
						total_tax_currency += line.amount_currency
						total += line.balance
						total_currency += line.amount_currency
						# print(total_untaxed,total_untaxed_currency,total,total_currency,'HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH')
					elif line.account_id.user_type_id.type in ('receivable', 'payable'):
						# Residual amount.
						total_residual += line.amount_residual
						total_residual_currency += line.amount_residual_currency
						# print(total_residual,total_residual_currency,'ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ')
				else:
					# === Miscellaneous journal entry ===
					if line.debit:
						total += line.balance
						total_currency += line.amount_currency
						# print(total,total_currency,'NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN')
			if move.type == 'entry' or move.is_outbound():
				sign = 1
			else:
				sign = -1
			move.amount_untaxed = (sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed))
			move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
			move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
			move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
			move.amount_untaxed_signed = -total_untaxed
			move.amount_tax_signed = -total_tax
			move.amount_total_signed = abs(total) if move.type == 'entry' else -total
			move.amount_residual_signed = total_residual

			currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
			is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

			# Compute 'invoice_payment_state'.
			if move.type == 'entry':
				move.invoice_payment_state = False
			elif move.state == 'posted' and is_paid:
				if move.id in in_payment_set:
					move.invoice_payment_state = 'in_payment'
				else:
					move.invoice_payment_state = 'paid'
			else:
				move.invoice_payment_state = 'not_paid'

	# @api.depends('line_ids.price_subtotal', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id', 'currency_id')
	# def _compute_invoice_taxes_by_group(self):
	# 	''' Helper to get the taxes grouped according their account.tax.group.
	# 	This method is only used when printing the invoice.
	# 	'''
	# 	for move in self:
	# 		lang_env = move.with_context(lang=move.partner_id.lang).env
	# 		tax_lines = move.line_ids.filtered(lambda line: line.tax_line_id)
	# 		res = {}
	# 		# There are as many tax line as there are repartition lines
	# 		done_taxes = set()
	# 		for line in tax_lines:
	# 			res.setdefault(line.tax_line_id.tax_group_id, {'base': 0.0, 'amount': 0.0})
	# 			res[line.tax_line_id.tax_group_id]['amount'] += line.gross_subtotal
	# 			tax_key_add_base = tuple(move._get_tax_key_for_group_add_base(line))
	# 			if tax_key_add_base not in done_taxes:
	# 				# The base should be added ONCE
	# 				res[line.tax_line_id.tax_group_id]['base'] += line.gross_subtotal
	# 				done_taxes.add(tax_key_add_base)
	# 		res = sorted(res.items(), key=lambda l: l[0].sequence)
	# 		move.amount_by_group = [(
	# 			group.name, amounts['amount'],
	# 			amounts['base'],
	# 			formatLang(lang_env, amounts['amount'], currency_obj=move.currency_id),
	# 			formatLang(lang_env, amounts['base'], currency_obj=move.currency_id),
	# 			len(res),
	# 			group.id
	# 		) for group, amounts in res]

	def action_post(self):
		res = super(AccountInvoice,self).action_post()
		for rec in self:
			if self.check_button == False:
				raise UserError(_('Please click Calculate Toatal Amount Button!!'))
		return  res

	def _check_balanced(self):
		''' Assert the move is fully balanced debit = credit.
		An error is raised if it's not the case.
		'''
		moves = self.filtered(lambda move: move.line_ids)
		if not moves:
			return

		# /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
		# are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
		# It happens as the ORM makes the create with the 'no_recompute' statement.
		self.env['account.move.line'].flush(['debit', 'credit', 'move_id'])
		self.env['account.move'].flush(['journal_id'])
		self._cr.execute('''
			SELECT line.move_id, ROUND(SUM(debit - credit), currency.decimal_places)
			FROM account_move_line line
			JOIN account_move move ON move.id = line.move_id
			JOIN account_journal journal ON journal.id = move.journal_id
			JOIN res_company company ON company.id = journal.company_id
			JOIN res_currency currency ON currency.id = company.currency_id
			WHERE line.move_id IN %s
			GROUP BY line.move_id, currency.decimal_places
			HAVING ROUND(SUM(debit - credit), currency.decimal_places) != 0.0;
		''', [tuple(self.ids)])

		query_res = self._cr.fetchall()
        # if query_res:
        #     ids = [res[0] for res in query_res]
        #     sums = [res[1] for res in query_res]
        #     raise UserError(_("Cannot create unbalanced journal entry. Ids: %s\nDifferences debit - credit: %s") % (ids, sums))
	# @api.depends('invoice_line_ids.price_subtotal',
 #                 'currency_id', 'company_id', 'invoice_date', 'type')
	# def _compute_amount(self):
	# 	for order in self:
	# 		order.gross_sales = sum(line.gross_total for line in order.invoice_line_ids)
	# 		round_curr = order.currency_id.round
	# 		amount_untaxed = amount_tax = amount_dis = gross_sales = 0.0
	# 		amount_trade = amount_qty = amount_spcl = 0.0
	# 		amt = 0.0
	# 		var = 0.0
	# 		for line in order.invoice_line_ids:
	# 			amount_trade += line.trade_amount
	# 			amount_qty += line.quantity_amount
	# 			amount_spcl += line.special_amount
	# 			if order.trade_dis or order.quantity_dis or order.special_dis:
	# 				amount_untaxed += line.price_subtotal
	# 				amount_tax = sum(line.credit for line in order.line_ids)
	# 				#print(amount_tax,'MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM')
	# 				var = (amount_untaxed)-(amount_trade + amount_qty + amount_spcl)
	# 				amt = (amount_tax) - (amount_trade + amount_qty + amount_spcl)
	# 			else:
	# 				amount_untaxed += line.price_subtotal
	# 				amount_tax = sum(line.credit for line in order.line_ids)
	# 		if order.trade_dis or order.quantity_dis or order.special_dis:
	# 			order.update({
	# 				'amount_untaxed': (amount_untaxed) - (amount_trade + amount_qty + amount_spcl),
	# 				'amount_total': amt,
	# 				# 'gross_sales': gross_sales#order.pricelist_id.currency_id.round(gross_sales)
	# 			})
	# 		else:
	# 			order.update({
	# 				'amount_untaxed': amount_untaxed,
	# 				'amount_total': amount_tax,
	# 				})
			# l.amount_untaxed = sum(line.price_subtotal for line in l.invoice_line_ids)
			# #l.amount_tax = sum(round_curr(line.amount_total) for line in l.tax_ids)
			# l.amount_total = l.amount_untaxed + l.amount_tax
			# l.amount_total = l.amount_untaxed
			# amount_total_company_signed = l.amount_total
			# amount_untaxed_signed = l.amount_untaxed
			# if l.currency_id and l.company_id and l.currency_id != l.company_id.currency_id:
			# 	currency_id = l.currency_id.with_context(date=l.invoice_date)
			# # 	amount_total_company_signed = currency_id.compute(l.amount_total, l.company_id.currency_id)
			# 	amount_untaxed_signed = currency_id.compute(l.amount_untaxed, l.company_id.currency_id)
			# sign = l.type in ['in_refund', 'out_refund'] and -1 or 1
			# l.amount_total_company_signed = amount_total_company_signed * sign
			# l.amount_total_signed = l.amount_total * sign
			# l.amount_untaxed_signed = amount_untaxed_signed * sign

	# @api.depends('partner_id','partner_shipping_id')
	# def func_fiscal_position(self):
	# 	for line in self:
	# 		if line.type == 'out_invoice':
	# 			if line.partner_shipping_id.state_id.code != line.partner_id.state_id.code:
	# 				line.fiscal_position_id = 1


	@api.depends('trade_dis','quantity_dis','special_dis','amount_untaxed','cal_done','state')
	def compute_display_button(self):
		for order in self:
			if order.state == 'draft':
				if order.trade_dis and order.quantity_dis and order.special_dis < 1:
					order.display_button = True
				else:
					order.display_button = True
			else:
				order.display_button = False

    

	
	# def _invoice_line_tax_values(self):
	# 	self.ensure_one()
	# 	tax_datas = {}
	# 	TAX = self.env['account.tax']
	# 	for line in self.mapped('invoice_line_ids'):
	# 		if not line.mtrs:
	# 			price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
	# 			tax_lines = line.invoice_line_tax_ids.compute_all(price_unit, line.invoice_id.currency_id, line.quantity, line.product_id, line.invoice_id.partner_id)['taxes']
	# 			for tax_line in tax_lines:
	# 				tax_line['tag_ids'] = TAX.browse(tax_line['id']).tag_ids.ids
	# 			tax_datas[line.id] = tax_lines
	# 		if line.mtrs:
	# 			price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
	# 			tax_lines = line.invoice_line_tax_ids.compute_all(price_unit, line.invoice_id.currency_id, line.mtrs, line.product_id, line.invoice_id.partner_id)['taxes']
	# 			for tax_line in tax_lines:
	# 				tax_line['tag_ids'] = TAX.browse(tax_line['id']).tag_ids.ids
	# 			tax_datas[line.id] = tax_lines
	# 	return tax_datas

	
    #displaying the categories in invoice on click of button
	def invoice_lines_create_discount(self):
		categ_grouped = self.get_invoice_product_discount_values()
		categ_lines = self.invoice_dis_line_ids.filtered('manual')
		self.check_button = True
		for line in categ_grouped.values():
			categ_lines += categ_lines.new(line)
		self.invoice_dis_line_ids = categ_lines
		self._trade_discount_cal()
		self._quantity_discount_cal()
		self._special_discount_cal()
		# print('DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')
		for l in self.invoice_line_ids:
			if self.trade_dis:
				self.line_ids = [(0,0,
		                                {
		                                'account_id':self.trade_discount_line_ids.account_id.id,
		                                'name':self.trade_discount_line_ids.name,
		                                #'payslip_id':self.id,
		                                'debit':l.trade_amount,
		                                })]
				for li in self.line_ids:
					if l.product_id == li.product_id and l.account_id == li.account_id:
						li.credit = l.trade_amount + l.credit
			if self.quantity_dis:
				self.line_ids = [(0,0,
		                                {
		                                'account_id':self.quantity_discount_line_ids.account_id.id,
		                                'name':self.quantity_discount_line_ids.name,
		                                #'payslip_id':self.id,
		                                'debit':l.quantity_amount,
		                                })]
				for li in self.line_ids:
					if l.product_id == li.product_id and l.account_id == li.account_id:
						li.credit = l.quantity_amount + l.credit
			if self.special_dis:
				self.line_ids = [(0,0,
		                                {
		                                'account_id':self.special_discount_line_ids.account_id.id,
		                                'name':self.special_discount_line_ids.name,
		                                #'payslip_id':self.id,
		                                'debit':l.special_amount,
		                                })]
				for li in self.line_ids:
					if l.product_id == li.product_id and l.account_id == li.account_id:
						li.credit = l.special_amount + l.credit
				# self.line_ids = [(1,self.line_ids,
		  #                               {
		  #                               # 'account_id':self.trade_discount_line_ids.account_id.id,
		  #                               # 'name':self.trade_discount_line_ids.name,
		  #                               #'payslip_id':self.id,
		  #                               'credit':l.trade_amount,
		  #                               })]
		#field is set to true to make button invisible once clicked
		self.display_button = False
		for line in self.invoice_line_ids:
			for rate in self.invoice_line_ids:
				if line.category_ids.id == rate.category_ids.id:
					if line.trade_discount != rate.trade_discount:
						raise models.ValidationError('Check Trade Discount')
					if line.quantity_discount != rate.quantity_discount:
						raise models.ValidationError('Check Quantity Discount')
					if line.special_discount != rate.special_discount:
						raise models.ValidationError('Check Special Discount')
		return


	@api.depends('invoice_line_ids.trade_amount','invoice_line_ids.quantity_amount','invoice_line_ids.special_amount','amount_untaxed','amount_tax')
	def _total_amount_invoice_discounts(self):
		for order in self:
			amount_trade = amount_qty = amount_spcl = 0.0
			for line in order.invoice_line_ids:
				#sum up of different discounts together from line part in invoice
				amount_trade += line.trade_amount
				amount_qty += line.quantity_amount
				amount_spcl += line.special_amount
			order.update({
                'amount_dis': amount_trade + amount_qty + amount_spcl,
                #negativity is set for display
                'trade_dis':-amount_trade,
                'quantity_dis':-amount_qty,
                'special_dis':-amount_spcl,
            })

	#Combining the categories to group and moving them to discount tab
	
	def get_invoice_product_discount_values(self):
		categ_grouped = {}
		for line in self.invoice_line_ids:
			if not line.mtrs: 
				price_unit = line.dis_price_unit * (1 - (line.discount or 0.0) / 100.0)
				categ = line.category_ids.compute_all_prod_invoice_discount(price_unit, line.trade_discount,line.quantity_discount,line.special_discount,self.currency_id, line.quantity, line.product_id, self.partner_id)['categ']
				for categ_line in categ:
					val = self._prepare_invoice_categ_line_vals(line, categ_line)
					key = self.env['item.category'].browse(categ_line['id']).get_grouping_key_categ(val)

					if key not in categ_grouped:
						categ_grouped[key] = val
					else:
						categ_grouped[key]['amount'] += val['amount']
						#fields are calculated from the invoice line and the discount percent is displayed in invoice discount
						#and the calculation is automated
						categ_grouped[key]['trade_discounts'] = val['trade_discounts']
						categ_grouped[key]['quantity_discount'] = val['quantity_discount']
						categ_grouped[key]['special_discount'] = val['special_discount']
			if line.mtrs:
				price_unit = line.dis_price_unit * (1 - (line.discount or 0.0) / 100.0)
				categ = line.category_ids.compute_all_prod_invoice_discount(price_unit, line.trade_discount,line.quantity_discount,line.special_discount,self.currency_id, line.mtrs, line.product_id, self.partner_id)['categ']
				for categ_line in categ:
					val = self._prepare_invoice_categ_line_vals(line, categ_line)
					key = self.env['item.category'].browse(categ_line['id']).get_grouping_key_categ(val)
					if key not in categ_grouped:
						categ_grouped[key] = val
					else:
						categ_grouped[key]['amount'] += val['amount']
						categ_grouped[key]['trade_discounts'] = val['trade_discounts']
						categ_grouped[key]['quantity_discount'] = val['quantity_discount']
						categ_grouped[key]['special_discount'] = val['special_discount']
		return categ_grouped

	def _prepare_invoice_categ_line_vals(self, line, categ_line):
		vals = {

            'invoice_categ_dis_id': self.id,
            'category': categ_line['id'],
            'trade_discount_id':3,
            'special_discount_id':2,
            'quantity_discount_id':1,
            'trade_discounts':categ_line['trade_discounts'],
            'quantity_discount':categ_line['quantity_discount'],
            'special_discount':categ_line['special_discount'],
            'sequence': categ_line['sequence'],
            'manual': False,
            'amount': categ_line['amount'],
    
        }
		return vals
    
	# @api.model
	# def invoice_line_move_line_get(self):
	# 	res = []
	# 	for line in self.invoice_line_ids:
	# 		if line.quantity==0:
	# 			continue
	# 		tax_ids = []
	# 		for tax in line.invoice_line_tax_ids:
	# 			tax_ids.append((4, tax.id, None))
	# 			for child in tax.children_tax_ids:
	# 				if child.type_tax_use != 'none':
	# 					tax_ids.append((4, child.id, None))
	# 		analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

	# 		move_line_dict = {
 #                'invl_id': line.id,
 #                'type': 'src',
 #                'name': line.name.split('\n')[0][:64],
 #                'price_unit': line.price_unit ,
 #                'quantity': line.quantity,
 #                #adding the discounted values to accounting so that the sales amount will be shown
 #                'price': line.price_subtotal + line.trade_amount + line.quantity_amount + line.special_amount,
 #                'account_id': line.account_id.id,
 #                'product_id': line.product_id.id,
 #                'uom_id': line.uom_id.id,
 #                'account_analytic_id': line.account_analytic_id.id,
 #                'tax_ids': tax_ids,
 #                'invoice_id': self.id,
 #                'analytic_tag_ids': analytic_tag_ids
 #            }
	# 		if line['account_analytic_id']:
	# 			move_line_dict['analytic_line_ids'] = [(0, 0, line._get_analytic_line())]
	# 		res.append(move_line_dict)
	# 	return res

	
	#@api.depends('invoice_line_ids')
	def _trade_discount_cal(self):
		#adding the sum total of trade discounts value same as tax calculation done in other info page
		if self.invoice_line_ids:
			trade_discount_grouped = self.get_trade_discount_values()
			trade_discount_lines = self.trade_discount_line_ids.filtered('manual')
			for line in trade_discount_grouped.values():
				trade_discount_lines += trade_discount_lines.new(line)
			self.trade_discount_line_ids = trade_discount_lines
		else:
			self.trade_discount_line_ids = False
		return

	
	#@api.depends('invoice_line_ids')
	def _quantity_discount_cal(self):
		#adding the sum total of quantity discounts value same as tax calculation done in other info page
		if self.invoice_line_ids:
			quantity_discount_grouped = self.get_quantity_discount_values()
			quantity_discount_lines = self.quantity_discount_line_ids.filtered('manual')
			for line in quantity_discount_grouped.values():
				quantity_discount_lines += quantity_discount_lines.new(line)
			self.quantity_discount_line_ids = quantity_discount_lines
		else:
			self.quantity_discount_line_ids = False
		return

	
	#@api.depends('invoice_line_ids')
	def _special_discount_cal(self):
		#adding the sum total of special discounts value same as tax calculation done in other info pageif self.invoice_line_ids:
		if self.invoice_line_ids:
			special_discount_grouped = self.get_special_discount_values()
			special_discount_lines = self.special_discount_line_ids.filtered('manual')
			for line in special_discount_grouped.values():
				special_discount_lines += special_discount_lines.new(line)
				#print(special_discount_lines,'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS')
			self.special_discount_line_ids = special_discount_lines
		else:
			self.special_discount_line_ids = False
		return

	
	def get_trade_discount_values(self):
		discount_grouped = {}
		for line in self.invoice_line_ids:
			price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
			discount = line.trade_discount_id.compute_all_trade_discount(price_unit,line.trade_amount, self.currency_id, line.quantity, line.product_id, self.partner_id)['discount']
			for discount_line in discount:
				val = self._prepare_trade_discount_line_vals(line, discount_line)
				key = self.env['sale.discount'].browse(discount_line['id']).get_grouping_key_trade_discount(val)
				if key not in discount_grouped:
					discount_grouped[key] = val
				else:
					discount_grouped[key]['amount'] += val['amount']
		return discount_grouped

	def _prepare_trade_discount_line_vals(self, line, discount_line):
		vals = {
            #'invoice_trade_discount_id': self.id,
            'name': discount_line['name'],
            'discount_id': discount_line['id'],
            'amount': discount_line['amount'],
            'manual': False,
            'sequence': discount_line['sequence'],
            #'account_analytic_id': discount_line['analytic'] and line.account_analytic_id.id or False,
            'account_id': self.type in ('out_invoice', 'in_invoice') and (discount_line['account_id'] or line.account_id.id) or (discount_line['refund_account_id'] or line.account_id.id),
        }
		# if not vals.get('account_analytic_id') and line.account_analytic_id and vals['account_id'] == line.account_id.id:
		# 	vals['account_analytic_id'] = line.account_analytic_id.id
		return vals

	@api.model
	def trade_discount_line_move_line_get(self):
		res = []
		# keep track of taxes already processed
		done_taxes = []
		# loop the invoice.tax.line in reversal sequence
		for discount_line in sorted(self.trade_discount_line_ids, key=lambda x: -x.sequence):
			if discount_line.amount_total:
				dis = discount_line.discount_id
				res.append({
					'invoice_discount_line_id': discount_line.id,
                    'discount_line_id': discount_line.discount_id.id,
                    'type': 'dis',
                    'name': discount_line.name,
                    'price_unit': discount_line.amount_total,
                    'quantity': 1,
                    'price': discount_line.amount_total,
                    'account_id': discount_line.account_id.id,
                    # 'account_analytic_id': discount_line.account_analytic_id.id,
                    'move_id': self.id,
                    'discount_id': [(6, 0, list(done_taxes))] if discount_line.discount_id.include_base_amount else []
                })
				done_taxes.append(dis.id)
		return res
#quantity Discount

	
	def get_quantity_discount_values(self):
		discount_grouped = {}
		for line in self.invoice_line_ids:
			price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
			discount = line.quantity_discount_id.compute_all_quantity_discount(price_unit,line.quantity_amount, self.currency_id, line.quantity, line.product_id, self.partner_id)['discount']
			for discount_line in discount:
				val = self._prepare_quantity_discount_line_vals(line, discount_line)
				key = self.env['sale.discount'].browse(discount_line['id']).get_grouping_key_quantity_discount(val)
				if key not in discount_grouped:
					discount_grouped[key] = val
				else:
					discount_grouped[key]['amount'] += val['amount']
		return discount_grouped

	def _prepare_quantity_discount_line_vals(self, line, discount_line):
		vals = {
            #'invoice_quantity_discount_id': self.id,
            'name': discount_line['name'],
            'discount_id': discount_line['id'],
            'amount': discount_line['amount'],
            'manual': False,
            'sequence': discount_line['sequence'],
            #'account_analytic_id': discount_line['analytic'] and line.account_analytic_id.id or False,
            'account_id': self.type in ('out_invoice', 'in_invoice') and (discount_line['account_id'] or line.account_id.id) or (discount_line['refund_account_id'] or line.account_id.id),
        }
		# if not vals.get('account_analytic_id') and line.account_analytic_id and vals['account_id'] == line.account_id.id:
		# 	vals['account_analytic_id'] = line.account_analytic_id.id
		return vals

	@api.model
	def quantity_discount_line_move_line_get(self):
		res = []
		# keep track of taxes already processed
		done_taxes = []
		# loop the invoice.tax.line in reversal sequence
		for discount_line in sorted(self.quantity_discount_line_ids, key=lambda x: -x.sequence):
			if discount_line.amount_total:
				dis = discount_line.discount_id
				res.append({
					'invoice_discount_line_id': discount_line.id,
                    'discount_line_id': discount_line.discount_id.id,
                    'type': 'dis',
                    'name': discount_line.name,
                    'price_unit': discount_line.amount_total,
                    'quantity': 1,
                    'price': discount_line.amount_total,
                    'account_id': discount_line.account_id.id,
                    #'account_analytic_id': discount_line.account_analytic_id.id,
                    'move_id': self.id,
                    'discount_id': [(6, 0, list(done_taxes))] if discount_line.discount_id.include_base_amount else []
                })
				done_taxes.append(dis.id)
		return res
#special discount


	
	def get_special_discount_values(self):
		discount_grouped = {}
		for line in self.invoice_line_ids:
			price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
			discount = line.special_discount_id.compute_all_special_discount(price_unit,line.special_amount, self.currency_id, line.quantity, line.product_id, self.partner_id)['discount']
			for discount_line in discount:
				val = self._prepare_special_discount_line_vals(line, discount_line)
				key = self.env['sale.discount'].browse(discount_line['id']).get_grouping_key_special_discount(val)
				if key not in discount_grouped:
					discount_grouped[key] = val
				else:
					discount_grouped[key]['amount'] += val['amount']
		return discount_grouped

	def _prepare_special_discount_line_vals(self, line, discount_line):
		for l in self:
			vals = {
	            'invoice_special_discount_id': l.id,
	            'name': discount_line['name'],
	            'discount_id': discount_line['id'],
	            'amount': discount_line['amount'],
	            'manual': False,
	            'sequence': discount_line['sequence'],
	            # 'account_analytic_id': discount_line['analytic'] and line.account_analytic_id.id or False,
	            'account_id': l.type in ('out_invoice', 'in_invoice') and (discount_line['account_id'] or line.account_id.id) or (discount_line['refund_account_id'] or line.account_id.id),
	        }

			#print(vals,'S***********************************************************************')
			# if not vals.get('account_analytic_id') and line.account_analytic_id and vals['account_id'] == line.account_id.id:
			# 	vals['account_analytic_id'] = line.account_analytic_id.id
			return vals

	@api.model
	def special_discount_line_move_line_get(self):
		res = []
		# keep track of taxes already processed
		done_taxes = []
		# loop the invoice.tax.line in reversal sequence
		for discount_line in sorted(self.special_discount_line_ids, key=lambda x: -x.sequence):
			if discount_line.amount_total:
				dis = discount_line.discount_id
				res.append({
					'invoice_discount_line_id': discount_line.id,
                    'discount_line_id': discount_line.discount_id.id,
                    'type': 'dis',
                    'name': discount_line.name,
                    'price_unit': discount_line.amount_total,
                    'special': 1,
                    'price': discount_line.amount_total,
                    'account_id': discount_line.account_id.id,
                    #'account_analytic_id': discount_line.account_analytic_id.id,
                    'move_id': self.id,
                    'discount_id': [(6, 0, list(done_taxes))] if discount_line.discount_id.include_base_amount else []
                })
				done_taxes.append(dis.id)
		return res

	


class AccountInvoiceLine(models.Model):
	_inherit ="account.move.line"



	
	# @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity','mtrs',
 #        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
 #        'invoice_id.date_invoice')
	# def _compute_price(self):
	# 	if not self.mtrs:
	# 		currency = self.invoice_id and self.invoice_id.currency_id or None
	# 		price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
	# 		taxes = False
	# 		if self.invoice_line_tax_ids:
	# 			taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
	# 		self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
	# 		self.gross_total = self.quantity * price
	# 		self.trade_amount = ((price*self.quantity)*self.trade_discount)/100
	# 		self.quantity_amount = ((price*self.quantity-((price*self.quantity)*self.trade_discount)/100)*self.quantity_discount)/100
	# 		self.special_amount = ((price*self.quantity-((((price*self.quantity)*self.trade_discount)/100)+((price*self.quantity-((price*self.quantity)*self.trade_discount)/100)*self.quantity_discount)/100))*self.special_discount)/100
	# 		self.price_total = taxes['total_included'] if taxes else self.price_subtotal
	# 		if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
	# 			price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
	# 		sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
	# 		self.price_subtotal_signed = price_subtotal_signed * sign
	# 	if self.mtrs:
	# 		currency = self.invoice_id and self.invoice_id.currency_id or None
	# 		price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
	# 		taxes = False
	# 		if self.invoice_line_tax_ids:
	# 			taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.mtrs, product=self.product_id, partner=self.invoice_id.partner_id)
	# 		self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.mtrs * price
	# 		self.gross_total = self.mtrs * price
	# 		self.trade_amount = ((price*self.mtrs)*self.trade_discount)/100
	# 		self.quantity_amount = ((price*self.mtrs-((price*self.mtrs)*self.trade_discount)/100)*self.quantity_discount)/100
	# 		self.special_amount = ((price*self.mtrs-((((price*self.mtrs)*self.trade_discount)/100)+((price*self.mtrs-((price*self.mtrs)*self.trade_discount)/100)*self.quantity_discount)/100))*self.special_discount)/100
	# 		self.price_total = taxes['total_included'] if taxes else self.price_subtotal
	# 		if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
	# 			price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
	# 		sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
	# 		self.price_subtotal_signed = price_subtotal_signed * sign

	category_ids = fields.Many2one('item.category',string="Item Category",related="product_id.item_category")
	#quantity = fields.Float(string='Quantity',default=1.0, digits='Product Unit of Measure')

	trade_discount = fields.Float(string='Trade Disc(%)', digits=dp.get_precision('Trade Discount'), default=0.0)
	trade_amount = fields.Float('Trade Disc(₹)', digits=dp.get_precision('Price'), default=0.0,compute="_compute_discount_values",store=True,track_visibility='always')
	trade_discount_id = fields.Many2many('sale.discount','trade_ids',store=True,string="Trade Discount" ,domain="[('discount_type','=','trade')]",default=lambda self: self.env['sale.discount'].search([('id', '=', 3)]).ids)
	quantity_discount = fields.Float(string='Quantity Disc(%)', digits=dp.get_precision('Quantity Discount'), default=0.0)
	quantity_amount = fields.Float('Quantity Disc(₹)', digits=dp.get_precision('Price'), default=0.0,compute="_compute_discount_values",store=True,track_visibility='always')
	quantity_discount_id = fields.Many2many('sale.discount','quantity_ids',store=True,string="Quantity Discount",domain="[('discount_type','=','quantity')]",default=lambda self: self.env['sale.discount'].search([('id', '=', 1)]).ids)
	special_discount = fields.Float(string='Special Disc(%)', digits=dp.get_precision('Special Discount'), default=0.0)
	special_amount = fields.Float('Special Disc(₹)', digits=dp.get_precision('Price'), default=0.0,compute="_compute_discount_values",store=True,track_visibility='always')
	special_discount_id = fields.Many2many('sale.discount','special_ids',store=True,string="Special Discount",domain="[('discount_type','=','special')]",default=lambda self: self.env['sale.discount'].search([('id', '=', 2)]).ids)

	dis_price_unit = fields.Float('Unit Price',digits=(16,3), default=0.0,store=True,track_visibility='always')
	#remove
	rep_price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Price'), default=0.0,store=True)
	total_prod_weight = fields.Float('Total Weight(kg)',store=True)
	price_unit = fields.Float('Price',digits='Product Price',readonly=False,store=True,track_visibility='always')
	gross_subtotal = fields.Monetary('Gross ', required=True, digits=dp.get_precision('Product Price'), default=0.0,store=True,track_visibility='always',compute='_calculate_dis_prices')
	#alternative meters
	mtrs = fields.Float(string="Alt.UOM value",digits=dp.get_precision('Meters'),default=0.00,readonly=False,store=True)
	alt_uom = fields.Many2one('uom.uom',string='Alt.Uom',readonly=False,related="product_id.product_tmpl_id.alternate_uom",store=True)
	gross_total = fields.Monetary(digits=dp.get_precision('Product Price'), string='Gross Subtotal', readonly=True, store=True,track_visibility='always',compute='_compute_gross_total_amount')

	discount_line_ids = fields.Many2many(
        'sale.discount.lines',
        'sale_discount_line_invoice_rel',
        'invoice_discount_line_id', 'discount_line_id',
        string='Sales Order Lines', readonly=True, copy=False)
	# price_subtotal = fields.Monetary(string='Subtotal', store=True, readonly=True,
 #        currency_field='always_set_currency_id',track_visibility='always',compute='_compute_sub_total_amount')

	@api.onchange('product_id','quantity','dis_price_unit','mtrs','rep_price_unit')
	def _Onchange_sub_total_amount(self):
		for line in self:
			t = 0
			tot = 0
			trade = quant = special = 0
			if line.mtrs:
				if line.trade_discount or line.quantity_discount or line.special_discount:
				# line.dis_price_unit = line.rep_price_unit * line.mtrs
					t = (line.dis_price_unit* line.mtrs)/line.quantity
					trade = (t * trade_discount) / 100
					quant = (t * quantity_discount) / 100
					special = (t * special_discount) / 100
					line.price_unit = (t) - (trade + quant + special)
				else:
					line.price_unit = (line.dis_price_unit* line.mtrs)/line.quantity


	# @api.depends('quantity','dis_price_unit','mtrs','rep_price_unit')
	# def _compute_sub_total_amount(self):
	# 	for line in self:
	# 		if line.mtrs:
	# 			# line.dis_price_unit = line.rep_price_unit * line.mtrs
	# 			line.price_subtotal = line.price_unit - (line.trade_amount + line.special_amount + line.quantity_amount)
	# 		else:
	# 			line.price_subtotal = False
	# 		else:
	# 			line.dis_price_unit = False
			# if not line.mtrs:
			# 	line.credit = line.dis_price_unit * line.quantity
			# 	line.debit = line.dis_price_unit * line.quantity
			# else:
			# 	line. = line.dis_price_unit * line.mtrs


	# def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
	# 	self.ensure_one()
	# 	print(price_unit,self.price_unit,'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
	# 	return self._get_price_total_and_subtotal_model(
	# 		price_unit=price_unit or self.price_unit,
	# 		quantity=quantity or self.quantity,
	# 		discount=discount or self.discount,
	# 		currency=currency or self.currency_id,
	# 		product=product or self.product_id,
	# 		partner=partner or self.partner_id,
	# 		taxes=taxes or self.tax_ids,
	# 		move_type=move_type or self.move_id.type,
	# 	)

	# @api.model
	# def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
	# 	''' This method is used to compute 'price_total' & 'price_subtotal'.
	# 	:param price_unit:  The current price unit.
	# 	:param quantity:    The current quantity.
	# 	:param discount:    The current discount.
	# 	:param currency:    The line's currency.
	# 	:param product:     The line's product.
	# 	:param partner:     The line's partner.
	# 	:param taxes:       The applied taxes.
	# 	:param move_type:   The type of the move.
	# 	:return:            A dictionary containing 'price_subtotal' & 'price_total'.
	# 	'''
	# 	res = {}

	# 	# Compute 'price_subtotal'.
	# 	price_unit_wo_discount = self.dis_price_unit * (1 - (discount / 100.0))
	# 	subtotal = quantity * price_unit_wo_discount

	# 	# Compute 'price_total'.
	# 	if taxes:
	# 		taxes_res = taxes._origin.compute_all(price_unit_wo_discount,
	# 		    quantity=self.mtrs, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
	# 		print(taxes_res,'********************************************')
	# 		res['price_subtotal'] = taxes_res['total_excluded']
	# 		res['price_total'] = taxes_res['total_included']
	# 	else:
	# 		res['price_total'] = res['price_subtotal'] = subtotal
	# 	return res



	@api.depends('product_id','quantity','dis_price_unit','mtrs')
	def _compute_gross_total_amount(self):
		for line in self:
			if not line.mtrs:
				line.gross_total = line.dis_price_unit * line.quantity
			else:
				line.gross_total = line.dis_price_unit * line.mtrs

	
	@api.onchange('product_id','quantity','dis_price_unit')
	def change_discount_price_unit(self):
		for line in self:
			line.price_unit = line.dis_price_unit
	# 		line.subtotal = line.mtrs * line.price_unit


	# @api.onchange('product_id','quantity')
	# def cal_alternative(self):
	# 	for line in self:
	# 		if line.product_id.product_tmpl_id.conversion:
	# 			line.mtrs = line.quantity * line.product_id.product_tmpl_id.conversion


	@api.depends('gross_total','quantity','mtrs','trade_discount','dis_price_unit','quantity_discount','special_discount')
	def _compute_discount_values(self):
		for order in self:
			if not order.mtrs:
				order.trade_amount = ((order.dis_price_unit*order.quantity)*order.trade_discount)/100
				order.quantity_amount = ((order.dis_price_unit*order.quantity-((order.dis_price_unit*order.quantity)*order.trade_discount)/100)*order.quantity_discount)/100
				order.special_amount = ((order.dis_price_unit*order.quantity-((((order.dis_price_unit*order.quantity)*order.trade_discount)/100)+((order.dis_price_unit*order.quantity-((order.dis_price_unit*order.quantity)*order.trade_discount)/100)*order.quantity_discount)/100))*order.special_discount)/100
			else:
				order.trade_amount=((order.dis_price_unit*order.mtrs)*order.trade_discount)/100
				order.quantity_amount = ((order.dis_price_unit*order.mtrs-((order.dis_price_unit*order.mtrs)*order.trade_discount)/100)*order.quantity_discount)/100
				order.special_amount = ((order.dis_price_unit*order.mtrs-((((order.dis_price_unit*order.mtrs)*order.trade_discount)/100)+((order.dis_price_unit*order.mtrs-((order.dis_price_unit*order.mtrs)*order.trade_discount)/100)*order.quantity_discount)/100))*order.special_discount)/100


	@api.depends('trade_amount','quantity_amount','special_amount','price_unit')
	def _calculate_dis_prices(self):
		for line in self:
			if not line.mtrs:
				line.gross_subtotal = ((line.dis_price_unit * line.quantity) - (line.trade_amount + line.quantity_amount + line.special_amount))
				#if line.quantity > 0:
					#line.price_unit = line.gross_subtotal / line.quantity
				# else:
				# 	raise exceptions.Warning(("Quantity is set to Zero."))
			else:
				line.gross_subtotal = ((line.dis_price_unit * line.mtrs) - (line.trade_amount + line.quantity_amount + line.special_amount))
				#line.price_unit = line.gross_subtotal / line.mtrs
