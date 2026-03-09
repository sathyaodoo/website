from odoo import models, fields, api, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    def init_daily_attendance(self, daily_attendance_date):
        self = self.filtered(lambda emp: emp.resource_calendar_id)
        daily_attendance_date = daily_attendance_date or fields.Datetime.now().date()
        daily_attendance = self.env['erpc.hr.daily.attendance']

        # YOU CAN USE THIS TO LOOP BETWEEN TWO DATES
        # start_date_str = "06/01/2024"
        # end_date_str = "06/30/2024"
        # start_datetime = datetime.datetime.strptime(start_date_str, "%m/%d/%Y")
        # end_datetime = datetime.datetime.strptime(end_date_str, "%m/%d/%Y")
        # current_datetime = start_datetime
        #
        # while current_datetime <= end_datetime:
        #     employee_ids.init_daily_attendance(current_datetime.date())
        #     current_datetime += datetime.timedelta(days=1)

        # Trigger synchronize_daily_attendance_for for each employee
        for employee_id in self:
            daily_attendance.synchronize_daily_attendance_for(employee_id, daily_attendance_date)
