from odoo import api, fields, models
from datetime import datetime, timedelta

class CrmLead(models.Model):
	_inherit = 'crm.lead'

	gst = fields.Char(string="GST")
	project_place = fields.Char(string="Project Place")


class Lead2OpportunityPartner(models.TransientModel):

    _inherit = 'crm.lead2opportunity.partner'	
    gst = fields.Char(string="GST")
    project_place = fields.Char(string="Project Place")

class SaleOrder(models.Model):

    _inherit = 'sale.order'	
    enquiry_date = fields.Datetime(string="Enquiry Date",related="opportunity_id.create_date") 