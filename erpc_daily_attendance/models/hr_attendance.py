from odoo import models, fields, api, _
from datetime import date, datetime


class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    def _synch_with_daily_attendance(self, old_check_in=False):
        for attendance_id in self:
            check_in = attendance_id.check_in
            daily_attendance = self.env['erpc.hr.daily.attendance']
            daily_attendance.synchronize_daily_attendance_for(attendance_id.employee_id, check_in.date())

            # Synchronize the old date as well if it exists
            if old_check_in:
                daily_attendance.synchronize_daily_attendance_for(attendance_id.employee_id, old_check_in.date())

    @api.model
    def create(self, vals):
        attendance_ids = super(HRAttendance, self).create(vals)
        attendance_ids._synch_with_daily_attendance()
        return attendance_ids

    def write(self, vals):
        check_in = False
        if 'check_in' in vals:
            check_in = self.check_in

        result = super().write(vals)
        self._synch_with_daily_attendance(check_in)
        return result
