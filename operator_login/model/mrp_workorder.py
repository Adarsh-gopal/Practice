import base64
import logging

from odoo import api, fields, models,exceptions,_
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError, ValidationError,Warning

_logger = logging.getLogger(__name__)


class MrpWorkorderProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    operator_id = fields.Many2one('man.power', 'Operator ID',compute="_onchange_work", store=True)
    shift = fields.Many2one('resource.calendar', store=True,compute="_onchange_work")

    
    @api.depends('workorder_id')
    def _onchange_work(self):
    	for line in self:
    		line.operator_id = line.workorder_id.production_id.operator_name.id
    		line.shift = line.workorder_id.production_id.shift.id


