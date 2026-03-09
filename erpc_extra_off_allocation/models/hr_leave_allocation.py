from odoo import api, fields, models, tools
from datetime import date, datetime, timedelta
from odoo.addons.resource.models.utils import HOURS_PER_DAY
import logging
import math

_log = logging.getLogger(__name__)


class HRLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    def allocate_extra_off_hours(self):
        _log.info(f"allocate_extra_off_hours:")

        # Get all active employees
        employee_ids = self.env['hr.employee'].search([('active', '=', True)])
        for employee_id in employee_ids:
            _log.info(f"employee_id: {employee_id.name}({employee_id})")

            # Get the reference for working hours and extra off days
            sunday_leave = self.env.ref('erpc_extra_off_allocation.erpc_hr_leave_type_sunday_leave')

            # Search for daily attendance records where work_entry_type_id is null and day is Sunday
            daily_attendance_ids = self.env['erpc.hr.daily.attendance'].search([
                ('employee_id', '=', employee_id.id),
                ('attendance_type', '=', 'present'),
                ('work_entry_type_id', '=', False),
                ('dayofweek', '=', '6'),
                ('actual_work_hours', '>', 0),
            ])

            for daily_attendance_id in daily_attendance_ids:
                _log.info(f"daily_attendance_id: {daily_attendance_id} at: {daily_attendance_id.attendance_date}")

                # Check if an allocation already exists for this date
                old_allocation_id = self.env['hr.leave.allocation'].search([
                    ('holiday_status_id', '=', sunday_leave.id),
                    ('employee_id', '=', employee_id.id),
                    ('date_from', '=', daily_attendance_id.attendance_date),
                ])

                if not old_allocation_id:
                    # Compute the number of days based on worked hours
                    # allocation_calendar = employee_id.sudo().resource_calendar_id
                    # number_of_days = daily_attendance_id.actual_work_hours / (allocation_calendar.hours_per_day or HOURS_PER_DAY)

                    # The client wants for each day to allocate one day, regardless the number of hours
                    number_of_days = 1

                    # Create the allocation with exact hours
                    _log.info(f"allocating number_of_days: {number_of_days}")
                    self.env['hr.leave.allocation'].create({
                        'name': f"Sunday Leave for {employee_id.name} on {daily_attendance_id.attendance_date}",
                        'holiday_status_id': sunday_leave.id,
                        'allocation_type': 'regular',
                        'holiday_type': 'employee',
                        'employee_id': employee_id.id,
                        'date_from': daily_attendance_id.attendance_date,
                        'number_of_days': number_of_days,
                    })

    def allocate_sunday_leave(self):
        # Calculate last Sunday
        today = fields.Datetime.today()
        weekday = today.weekday()
        last_sunday = today - timedelta(days=weekday + 1)

        syrian_employees = self.env['hr.employee'].search([('country_id.id', '=', self.env.ref('base.sy').id),
                                                           ('contract_id.lives_in_yokohama', '=', 'yes')
                                                           ])
        for employee in syrian_employees:
            leave_ids = self.env['hr.leave'].search([
                ('employee_id', '=', employee.id),
                ('date_to', '>=', last_sunday),
                ('date_from', '<=', last_sunday),
            ])

            leave_type = self.env.ref('erpc_extra_off_allocation.erpc_hr_leave_type_sunday_leave')
            if not leave_ids and leave_type:
                allocation = self.env['hr.leave.allocation'].create({
                    'name': f"Sunday Leave for {employee.name} ({last_sunday})",
                    'employee_id': employee.id,
                    'holiday_status_id': leave_type.id,
                    'number_of_days': 1,
                    'allocation_type': 'regular',
                })
                allocation.action_validate()
