from odoo import models, fields, api


class ERPCHRDailyAttendanceLine(models.Model):
    _name = 'erpc.hr.daily.attendance.line'
    _order = "check_in desc"

    daily_attendance_id = fields.Many2one('erpc.hr.daily.attendance', "Daily Attendance", readonly=True, ondelete='cascade')
    attendance_id = fields.Many2one('hr.attendance', "Related Attendance", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", related='attendance_id.employee_id', store=True)
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id', store=True)
    check_in = fields.Datetime(string="Check In", related='attendance_id.check_in', store=True)
    check_out = fields.Datetime(string="Check Out", related='attendance_id.check_out', store=True)
    worked_hours = fields.Float(string='Worked Hours', related='attendance_id.worked_hours', store=True)
