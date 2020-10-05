from odoo import models, fields, api, _

class CustomFields(models.Model):
	_name = "custom.fields"
	name= fields.Char(string='Name',store=True ,index=True,ondelete='cascade')


class Custom(models.Model):
    _name = 'crm.custom'
    name= fields.Char(string='Category here',store=True )

class BloodGroup(models.Model):
	_name = "custom.fields.bgroup"
	name = fields.Char(string='Group',store=True ,index=True,ondelete='cascade')

class IndustryGroup(models.Model):
	_name = "custom.fields.industrygroup"
	name= fields.Char(string='Group',store=True ,index=True,ondelete='cascade')

class IndustryType(models.Model):
	_name = "custom.fields.industrytype"
	name= fields.Char(string='Type',store=True ,index=True,ondelete='cascade')

class CrmFields(models.Model):
    _name = 'custom.fields.crm'
    name= fields.Char(string='Category here',store=True ,ondelete='cascade')