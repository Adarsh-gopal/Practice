from datetime import datetime, timedelta

from odoo import api, models, fields, _, exceptions
from dateutil.relativedelta import relativedelta
from time import strptime
from odoo.exceptions import UserError, ValidationError,Warning

class BloodGroup(models.Model):
	_name = "custom.fields.bgroup"
	name = fields.Char(string='Group',store=True ,index=True,ondelete='cascade')



class HrEmployee(models.Model):
	_inherit = 'hr.employee'


	joining_date = fields.Date(string='Joining Date')
	epf_uan_no = fields.Char(string='EPF UAN Number', size=12)
	esi_number = fields.Char(string='ESI Number')
	age = fields.Char(string='Age', size=3, compute='_compute_age')
	caste = fields.Char(string='Caste')
	religion = fields.Many2one('reli.name', string='Religion')
	street = fields.Char(string='Alternative Address')
	street2 = fields.Char(string='Street2')
	city = fields.Char(string='City')
	country = fields.Many2one('res.country',string='Country')
	state = fields.Many2one('res.country.state',string='State')
	zip = fields.Char(string='Zip')
	handicap = fields.Boolean(string='Handicap')
	height = fields.Float(string='Height')
	weight = fields.Float(string='Weight')
	personal_mark_of_identification = fields.Char(string='Personal Mark of Identification')
	righteye = fields.Char(string='Right Eye',size=6)
	lefteye = fields.Char(string='Left Eye',size=6)
	total_no_of_dependents = fields.Integer(string='Total No. Of Dependents')
	registeration_number = fields.Char(string='Registration Number')
	driving_license = fields.Char(string='Driving License')
	languages = fields.Many2one('cas.name', string='Languages')
	rite = fields.Boolean(string='Read')
	wr = fields.Boolean(string='Write')
	speak = fields.Boolean(string='Speak')
	relation = fields.Many2one('relation.name', string='Relation')
	name = fields.Char(string='Name')
	the_age = fields.Char(string='Age', size=3)
	qualification = fields.Many2one('qual.name', string='Qualification')
	occupation = fields.Char(string='Occupation')
	qualification = fields.Many2one('qualify.name',string='Qualification')
	college = fields.Char(string='College')
	year_of_passing = fields.Date(string='Year of passing')
	percentage = fields.Float(string='Percentage')
	period_from = fields.Date(string='Period From')
	period_to = fields.Date(string='Period To')
	organization = fields.Char(string='Organization')
	designation = fields.Many2one('designation.name', string='Designation')
	ctc = fields.Float(string='CTC')
	reason_for_leaving = fields.Many2one('reason.name', string='Reason For Leaving')
	esi_applicable = fields.Boolean(string='ESI Applicable')
	vpf_applicable = fields.Boolean(string='VPF Applicable')
	vpf_amount = fields.Float(string='VPF Amount')
	one = fields.One2many('lang.unknown','many')
	two = fields.One2many('education.details','edu_details_id')
	three = fields.One2many('family.details','family')
	four = fields.One2many('experience.details','experience')
	date_of_relieving = fields.Date(string='Date of Relieving')
	date_of_resignation = fields.Date(string='Date of Resignation')
	blood_group=fields.Many2one('custom.fields.bgroup',string='Blood Group',store=True )

	@api.depends('birthday')
	def _compute_age(self):
		for rec in self:
			if rec.birthday:
				dt = rec.birthday
				d1 = datetime.strptime(dt, "%Y-%m-%d").date()
				d2 = datetime.today()
				rd = relativedelta(d2, d1)
				rec.age = str(rd.years) + ' years' 

	@api.constrains('epf_uan_no')
	def _check_number(self):
		epf_uan_no = self.epf_uan_no
		if self.epf_uan_no and len(str(abs(int(self.epf_uan_no))))<12:
			raise ValidationError(_("EPF UAN No. should be not be more than 12 digits"))

	@api.constrains("joining_date","birthday")
	def _check_period(self):
		for rec in self:
			if rec.joining_date < rec.birthday:
				raise ValidationError('Sorry, Joining date must be greater than birthdate')


	@api.constrains('age')
	def _check_age(self):
		if self.age and len(str(abs(int(self.age))))>3:
			raise ValidationError(_("Age must be in 3 digits"))

	
class LanguagesKnown(models.Model):
	_name = 'lang.unknown'

	many = fields.Many2one('hr.employee')

	languages = fields.Many2one('cas.name', string='Languages')
	rite = fields.Boolean(string='Read')
	wr = fields.Boolean(string='Write')
	speak = fields.Boolean(string='Speak')

class FamilyDetails(models.Model):
	_name = 'education.details'

	edu_details_id = fields.Many2one('hr.employee')
	relation = fields.Many2one('relation.name', string='Relation')
	name = fields.Char(string='Name')
	the_age = fields.Char(string='Age', size=3)
	qualification = fields.Many2one('qual.name', string='Qualification')
	occupation = fields.Char(string='Occupation')

	@api.constrains('the_age')
	def _check_age(self):
		if self.the_age and len(str(abs(int(self.the_age))))>3:
			raise ValidationError(_("Age must be in 3 digits"))


class EmployeesFamilyDetails(models.Model):
	_name = 'family.details'

	family = fields.Many2one('hr.employee')
	qualification = fields.Many2one('qualify.name', string='Qualification')
	college = fields.Char(string='College')
	year_of_passing = fields.Date(string='Year Of Passing')
	percentage = fields.Float(string='Percentage')

	@api.constrains('percentage')
	def _check_age(self):
		if self.percentage>100.00:
			raise ValidationError(_("Percentage should be with in 100"))

	

class EmployeesExpDetails(models.Model):
	_name = 'experience.details'

	experience = fields.Many2one('hr.employee')
	period_from = fields.Date(string='Period From')
	period_to = fields.Date(string='Period To')
	organization = fields.Char(string='Organization')
	designation = fields.Many2one('designation.name', string='Designation')
	ctc = fields.Float(string='CTC')
	reason_for_leaving = fields.Many2one('reason.name', string='Reason For Leaving')

	@api.constrains("period_to","period_from")
	def _check_period(self):
		for rec in self:
			if rec.period_to < rec.period_from:
				raise ValidationError('Sorry, Period From cannot be greater than Period To')


class Qualification(models.Model):
	_name = 'qual.name'

	name = fields.Char(string='Qualification')


class Qualifications(models.Model):
	_name = "qualify.name"


	name = fields.Char(string="Qualification", store=True)

class Castes(models.Model):
	_name = 'cas.name'

	name = fields.Char(string='Languages')	

class Designation(models.Model):
	_name = 'designation.name'


	name = fields.Char(string='Designation Name')


class Relationship(models.Model):
	_name = 'reli.name'

	name = fields.Char(string='Religion')

class Relation(models.Model):
	_name = 'relation.name'

	name = fields.Char(string='Relation')

class ReasonLeaving(models.Model):
	_name = 'reason.name'

	name = fields.Char(string='Reason For Leaving')
