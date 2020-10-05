import base64
import logging

from odoo import api, fields, models,exceptions,_
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError, ValidationError,Warning

_logger = logging.getLogger(__name__)


class ManufacturingInherit(models.Model):
    _inherit = "mrp.production"

    operator_name = fields.Many2one('man.power', domain="[('category_types','=','operator')]",string="Operator ID")
    logger_name = fields.Char(string="Operator Name",related="operator_name.logger_id",store=True,readonly=True)
    cutter_id = fields.Many2many('man.power', domain="[('category_types','=',('cutter','helper'))]",string="Cutter man / Helper")
    shift = fields.Many2one('resource.calendar',string="Shift",domain="[('z_production_schedule', '=', True)]")
    log_ids = fields.One2many('operator.log','log_id')
    workcenter_id = fields.Many2one('mrp.workcenter',string="Machine Number")
    button_enable_change_wc = fields.Boolean(string="Change Work center",store=True,compute="compute_change_workcenter_validate")
    z_operator_assign = fields.Char(string="Condition Field")


    

# call this function in the stock.move.line as compute. Need to declare in stock.move.line
    
    @api.depends('workcenter_id')
    def compute_change_workcenter_validate(self):
    	for line in self:
    		mo_workorder = self.env['mrp.workorder'].search([('production_id', '=', line.id)])
    		for wc in mo_workorder:
    			if wc.workcenter_id == line.workcenter_id:
    				line.button_enable_change_wc = True
    			else:
    				line.button_enable_change_wc = False


    def button_update_machine(self):
    	for line in self:
    		if line.state == 'confirmed':
    			raise exceptions.Warning(("Plan the process before updating."))
    		else:
	    		if line.workcenter_id:
		    		mo_workorder = self.env['mrp.workorder'].search([('production_id', '=', line.id)])
		    		for wc in mo_workorder:
		    			wc.update({'workcenter_id':line.workcenter_id.id})
		    		line.button_enable_change_wc = True
		    	else:
		    		raise exceptions.Warning(("Enter the Machine Number before updating"))
		    		    	

class OperatorLogTrack(models.Model):
    _name = "operator.log"

    log_id = fields.Many2one('mrp.production')
    name = fields.Many2one('man.power',domain="[('category_types','=','operator')]",string="Operator ID",readonly=True)
    workcenter_id = fields.Many2one('mrp.workcenter',string="Machine Number",readonly=True)
    shift = fields.Many2one('resource.calendar',string="Shift",readonly=True)
    login_time = fields.Datetime('Login Time', copy=False,index=True,readonly=True)
    cutter_id = fields.Many2many('man.power', readonly=True,string="Cutter man / Helper")
    logger_name=fields.Char(string="Operator Name",related="name.logger_id")



