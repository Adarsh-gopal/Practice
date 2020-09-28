#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

class HrEmployee(models.Model):
	_inherit='hr.employee'
	z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',help="The analytic account related to a Invoice.")
	z_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

class HrPayslip(models.Model):
	_inherit = 'hr.payslip'

	z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',help="The analytic account related to a Invoice.",related='employee_id.z_analytic_account_id')

	
	def action_payslip_done(self):
		res = super(HrPayslip, self).action_payslip_done()
		precision = self.env['decimal.precision'].precision_get('Payroll')

		for slip in self:
			line_ids = []
			debit_sum = 0.0
			credit_sum = 0.0
			date = slip.date or slip.date_to

			name = _('Payslip of %s') % (slip.employee_id.name)
			move_dict = {
                'narration': name,
                'ref': slip.number,
                'z_analytic_account_id':slip.employee_id.z_analytic_account_id.id,
                'journal_id': slip.journal_id.id,
                'date': date,
			}
			for line in slip.details_by_salary_rule_category:
				amount = slip.credit_note and -line.total or line.total
				if float_is_zero(amount, precision_digits=precision):
					continue
				debit_account_id = line.salary_rule_id.account_debit.id
				credit_account_id = line.salary_rule_id.account_credit.id
				analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in slip.employee_id.z_analytic_tag_ids]

				if debit_account_id:
					debit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=False),
                        'account_id': debit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amount > 0.0 and amount or 0.0,
                        'credit': amount < 0.0 and -amount or 0.0,
                        'analytic_account_id': slip.employee_id.z_analytic_account_id.id,
                        'analytic_tag_ids':analytic_tag_ids,
                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
					})
					line_ids.append(debit_line)
					debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']


				if credit_account_id:
					credit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=True),
                        'account_id': credit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amount < 0.0 and -amount or 0.0,
                        'credit': amount > 0.0 and amount or 0.0,
                        'analytic_account_id': slip.employee_id.z_analytic_account_id.id,
                        'analytic_tag_ids':analytic_tag_ids,
                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
					})
					line_ids.append(credit_line)
					credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

			if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
				acc_id = slip.journal_id.default_credit_account_id.id
				if not acc_id:
					raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (slip.journal_id.name))
				adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
				})
				line_ids.append(adjust_credit)

			elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
				acc_id = slip.journal_id.default_debit_account_id.id
				if not acc_id:
					raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (slip.journal_id.name))
				adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
				})
				line_ids.append(adjust_debit)
			move_dict['line_ids'] = line_ids
			move = self.env['account.move'].create(move_dict)
			slip.write({'move_id': move.id, 'date': date})
			move.post()
		return res

