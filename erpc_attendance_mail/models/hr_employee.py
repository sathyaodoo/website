from odoo import api, fields, models
from datetime import datetime, time


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    send_attendance_reminder = fields.Selection([('yes', 'YES'), ('no', 'NO')], 'Attendance Reminder', required=True, help="Choose Yes to receive notification in attendance reminder about this employee")

    def check_in_today(self):
        today = fields.Date.today()
        attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', self.id),
            ('check_in', '>=', datetime.combine(today, time(0, 0, 0))),  # Start of today
            ('check_in', '<=', datetime.combine(today, time(23, 59, 59))),  # End of today
        ])
        return bool(attendance)

    def check_out_today(self):
        today = fields.Date.today()
        attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', self.id),
            ('check_out', '>=', datetime.combine(today, time(0, 0, 0))),  # Start of today
            ('check_out', '<=', datetime.combine(today, time(23, 59, 59))),  # End of today
        ])
        return bool(attendance)

    def has_time_off_today(self):
        today = fields.Date.today()
        time_off_requests = self.env['hr.leave'].search([
            ('employee_id', '=', self.id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('date_from', '<=', today),
            ('date_to', '>=', today)
        ])
        return bool(time_off_requests)
