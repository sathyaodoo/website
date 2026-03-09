import logging

from collections import namedtuple, defaultdict

from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from math import ceil
from pytz import timezone, UTC

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG

from odoo import api, Command, fields, models, tools
from odoo.addons.base.models.res_partner import _tz_get
from odoo.tools.date_utils import float_to_time
from odoo.addons.resource.models.utils import HOURS_PER_DAY


from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.float_utils import float_round, float_compare
from odoo.tools.misc import format_date
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    successive_leave = fields.Boolean(string="Successive Leave")


class HrLeave(models.Model):
    _inherit = "hr.leave"

    # def _get_duration(self, check_leave_type=True, resource_calendar=None):
    #     self.ensure_one()
    #     resource_calendar = resource_calendar or self.resource_calendar_id

    #     if not self.date_from or not self.date_to or not resource_calendar:
    #         return (0, 0)

    #     hours, days = 0, 0

    #     if self.employee_id:
    #         # We force the company in the domain as we are more than likely in a compute_sudo
    #         domain = [('time_type', '=', 'leave'),
    #                   ('company_id', 'in', self.env.companies.ids + self.env.context.get('allowed_company_ids', [])),
    #                   # When searching for resource leave intervals, we exclude the one that
    #                   # is related to the leave we're currently trying to compute for.
    #                   '|', ('holiday_id', '=', False), ('holiday_id', '!=', self.id)]

    #         if self.leave_type_request_unit == 'day' and check_leave_type:
    #             # list of tuples (day, hours) from the employee's work time per day
    #             work_time_per_day_list = self.employee_id.list_work_time_per_day(self.date_from, self.date_to, calendar=resource_calendar, domain=domain)

    #             # Set of dates already included in work_time_per_day_list (e.g., for checking Sundays)
    #             included_days = {day.date() for day, _ in work_time_per_day_list}

    #             _logger.info(f"\n\n\\n\n\n\n\n\ work_time_per_day_list {work_time_per_day_list}")
    #             _logger.info(f"\n\n\\n\n\n\n\n\ included_days {included_days}")
    #             # Loop over the date range, checking each day
    #             current_day = self.date_from
    #             while current_day <= self.date_to:
    #                 if current_day.weekday() == 6 and current_day.date() not in included_days:
    #                     hours += 9
    #                     days += 1
    #                     _logger.info(f"\n\n\n\n\\n\n\n HEREEEEE")
    #                 elif current_day.date() in included_days:
    #                     _logger.info(f"\n\n\n\n\\n\n\nHELLOOOO")
    #                     day_hours = next(h for d, h in work_time_per_day_list if d.date() == current_day.date())
    #                     hours += day_hours
    #                     days += 1
    #                 current_day += timedelta(days=1)

    #             _logger.info(f"\n\n\n\n\\n\n\nCalculated hours: {hours}, Calculated days: {days}")
    #         else:
    #             work_days_data = self.employee_id._get_work_days_data_batch(self.date_from, self.date_to, domain=domain, calendar=resource_calendar)[self.employee_id.id]
    #             hours, days = work_days_data['hours'], work_days_data['days']
    #             _logger.info(f"\n\n\\n\n\n\n\n\ work_days_data {work_days_data}")
    #             # _logger.info(f"\n\n\\n\n\n\n\n\ included_days {included_days}")
    #     else:
    #         today_hours = resource_calendar.get_work_hours_count(
    #             datetime.combine(self.date_from.date(), time.min),
    #             datetime.combine(self.date_from.date(), time.max),
    #             False)
    #         hours = resource_calendar.get_work_hours_count(self.date_from, self.date_to)

    #         _logger.info(f"\n\n\\n\n\n\nCalculated work hours: {hours}")
    #         days = hours / (today_hours or HOURS_PER_DAY)
    #         _logger.info(f"\n\n\n\\n\n\nCalculated days: {days}")

    #     if self.leave_type_request_unit == 'day' and check_leave_type:
    #         days = ceil(days)

    #     return (days, hours)

    @api.depends(
        "date_from", "date_to", "resource_calendar_id", "holiday_status_id.request_unit"
    )
    def _compute_duration(self):
        for holiday in self:
            if holiday.holiday_status_id.successive_leave:
                days, hours = holiday._get_duration()

                start_date = holiday.date_from
                end_date = holiday.date_to

                delta = end_date - start_date
                total_days_inclusive = delta.days + 1
                # total_hours = total_days_inclusive * 24

                holiday.number_of_hours = hours
                holiday.number_of_days = total_days_inclusive
            else:
                super(HrLeave, holiday)._compute_duration()
