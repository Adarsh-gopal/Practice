from odoo import api, fields, models,_

class Lead(models.Model):
	_name = "crm.lead"
	_inherit="crm.lead"
	industry_group=fields.Many2one('custom.fields.industrygroup', string="Industry Group",store=True)
	industry_type=fields.Many2one('custom.fields.industrytype',string="Industry Vertical",store=True)

