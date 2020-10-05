import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Holiday(models.AbstractModel):
    _name = 'report.man_power.report_man_power'

    
    def daily_attendance(self, form, day, student):
        attend_month = self.env['roster.type'
                                ].browse(self._context.get('active_id'))
        st_date = attend_month.month.date_start
#        end_dt = attend_month.month.date_stop
        attend_obj = self.env['man.attendance']
        start_date = datetime.strptime(st_date, '%Y-%m-%d')
        if day - start_date.day >= 0:
            attend_date = start_date + rd(days=+day - start_date.day)
        else:
            attend_date = start_date + rd(days=+day + start_date.day)
        sheets = attend_obj.search([('state', '=', 'validate'),
                                    ('date',
                                     '=', attend_date)])
        flag = 'A'
        for sheet in sheets:
            for line in sheet.student_ids:
                if line.stud_id.id == student.id:
                    if line.is_present:
                        flag = 'P'
        return flag

    @api.model
    def get_report_values(self, docids, data=None):
        attendance_data = self.env['ir.actions.report']._get_report_from_name(
            'school_attendance.attendance_month')
        active_model = self._context.get('active_model')
        docs = self.env[active_model
                        ].browse(self._context.get('active_ids'))
        return {'doc_ids': docids,
                'doc_model': attendance_data.model,
                'data': data,
                'docs': docs,
                'get_header_data': self.get_header_data,
                'daily_attendance': self.daily_attendance,
                'get_student': self.get_student,
                }
