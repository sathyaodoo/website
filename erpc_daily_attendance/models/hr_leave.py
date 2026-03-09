from odoo import api, Command, fields, models, tools
from datetime import datetime, timedelta


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'

    def action_validate(self):
        result = super().action_validate()
        for rec in self:
            date_from = rec.date_from.date()
            date_to = rec.date_to.date()
            daily_attendance_date = date_from
            while daily_attendance_date <= date_to:
                rec.employee_id.init_daily_attendance(daily_attendance_date)
                daily_attendance_date += timedelta(days=1)
        return result

    def action_refuse(self):
        result = super().action_refuse()
        for rec in self:
            date_from = rec.date_from.date()
            date_to = rec.date_to.date()
            daily_attendance_date = date_from
            while daily_attendance_date <= date_to:
                rec.employee_id.init_daily_attendance(daily_attendance_date)
                daily_attendance_date += timedelta(days=1)
        return result
