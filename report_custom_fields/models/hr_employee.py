from odoo import models, fields, api, _




class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit="hr.employee"
    pan_no= fields.Char(string='PAN No',store=True)
   

    @api.constrains('pan_no')
    def _check_pan_number(self):
    	for rec in self:
    		if rec.pan_no and len(rec.pan_no) > 10:
    			raise models.ValidationError(_("Pan number cannot be more than 10 digits..."))
    		return True





