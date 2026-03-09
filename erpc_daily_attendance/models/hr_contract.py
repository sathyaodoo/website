from odoo import fields, models, api
from odoo.tools.intervals import Intervals
from collections import defaultdict
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import pytz


class HrVersion(models.Model):
    _inherit = 'hr.version'

    work_entry_source = fields.Selection(
        selection_add=[('daily_attendance', 'Daily Attendance')],
        ondelete={'daily_attendance': lambda recs: recs.write({'work_entry_source': 'calendar'})}, readonly=True,
        default='daily_attendance')

    def _get_interval_work_entry_type(self, interval):
        self.ensure_one()
        if self.work_entry_source == 'daily_attendance':
            return interval[2]
        return super()._get_interval_work_entry_type(interval)

    def _get_more_vals_attendance_interval(self, interval):
        # TODO: The overtime and the undertime should be handled here,
        #  but for now keep it as query on payslip generate
        result = super()._get_more_vals_attendance_interval(interval)
        return result

    def _get_attendance_intervals(self, start_dt, end_dt):
        daily_attendance_based_contracts = self.filtered(lambda c: c.work_entry_source == 'daily_attendance')
        search_domain = [
            ('employee_id', 'in', daily_attendance_based_contracts.employee_id.ids),
            ('state', '=', 'validated'),
            ('tuned_start_dt', '<', end_dt),
            ('tuned_end_dt', '>', start_dt),
        ]
        resource_ids = daily_attendance_based_contracts.employee_id.resource_id.ids
        daily_attendance_slots = self.env['erpc.hr.daily.attendance'].sudo().search(
            search_domain) if daily_attendance_based_contracts else self.env['erpc.hr.daily.attendance']
        intervals = defaultdict(list)

        for daily_attendance_slot in daily_attendance_slots:
            # The dates in the intervals should be localized
            planned_start_dt = daily_attendance_slot.planned_start_dt

            # Working Hours
            if daily_attendance_slot.core_work_hours > 0:
                working_start_dt = planned_start_dt
                working_end_dt = working_start_dt + relativedelta(hours=daily_attendance_slot.core_work_hours)
                intervals[daily_attendance_slot.resource_id.id].append((
                    pytz.utc.localize(working_start_dt),
                    pytz.utc.localize(working_end_dt),
                    self.env.ref('erpc_daily_attendance.erpc_hr_work_entry_type_working_hours'),
                ))

        mapped_intervals = {r: Intervals(intervals[r]) for r in resource_ids}
        mapped_intervals.update(super()._get_attendance_intervals(start_dt, end_dt))
        return mapped_intervals
