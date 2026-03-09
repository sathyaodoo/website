from odoo import models, fields, api
from datetime import date, datetime
from collections import defaultdict
import pytz
import calendar
import logging

_log = logging.getLogger(__name__)


class ERPCHRDailyAttendance(models.Model):
    _name = 'erpc.hr.daily.attendance'
    _rec_name = 'employee_id'
    _order = "attendance_date desc, employee_id"
    _sql_constraints = [
        (
            'unique_daily_attendance',
            'unique(employee_id, attendance_date)',
            'An employee can have only single "daily attendance" record per day.'
        )
    ]

    attendance_date = fields.Date(string="Date", required=True, readonly=True)
    attendance_date_start = fields.Datetime(string="Date Start", required=True, readonly=True)
    attendance_date_end = fields.Datetime(string="Date End", required=True, readonly=True)
    total_overtime_undertime = fields.Float('Total Overtime Undertime', compute='compute_total_overtime_undertime', store=True)
    work_entry_type_id = fields.Many2one('hr.work.entry.type')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True)
    company_id = fields.Many2one('res.company', string="Company", related='employee_id.company_id', store=True)
    version_id = fields.Many2one('hr.version', string="Contract", related='employee_id.version_id', store=True)
    resource_id = fields.Many2one('resource.resource', string="Resource", related='employee_id.resource_id', store=True)
    resource_calendar_id = fields.Many2one('resource.calendar', string="Working Schedule", related='employee_id.resource_calendar_id', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('cancelled', 'Cancelled')
    ], default='draft')

    attendance_ids = fields.One2many('erpc.hr.daily.attendance.line', 'daily_attendance_id', string='Attendances', readonly=True)
    closed_attendance_ids = fields.One2many('erpc.hr.daily.attendance.line', 'daily_attendance_id', string='Attendances', compute='_compute_closed_attendance_ids')
    attendance_type = fields.Selection([
        ('absent', 'Absent'),
        ('present', 'Present')
    ], compute='_compute_attendance_type', store=True)

    planned_start_dt = fields.Datetime(string="Schedule Start", readonly=True)
    planned_end_dt = fields.Datetime(string="Schedule End", readonly=True)
    planned_work_hours = fields.Float(string='Schedule Work Hours', readonly=True)
    planned_break_hours = fields.Float(string='Schedule Break Hours', compute='_compute_planned_break_hours', store=True, readonly=True)

    actual_start_dt = fields.Datetime(string="Actual Start", compute='_compute_actual_start_end_dt', store=True, readonly=True)
    actual_end_dt = fields.Datetime(string="Actual End", compute='_compute_actual_start_end_dt', store=True, readonly=True)
    actual_break_hours = fields.Float(string='Actual Break Hours', compute='_compute_pre_core_post_work_hours_actual_tuned_break_hours', store=True, readonly=True)
    actual_work_hours = fields.Float(string='Actual Work Hours', compute='_compute_actual_work_hours', store=True, readonly=True)

    tuned_start_dt = fields.Datetime(string="Tuned Start", compute='_compute_tuned_start_end_dt', store=True, readonly=False)
    tuned_end_dt = fields.Datetime(string="Tuned End", compute='_compute_tuned_start_end_dt', store=True, readonly=False)
    tuned_break_hours = fields.Float(string='Tuned Break Hours', compute='_compute_pre_core_post_work_hours_actual_tuned_break_hours', store=True, readonly=False)
    tuned_work_hours = fields.Float(string='Tuned Work Hours', compute='_compute_tuned_work_hours', store=True, readonly=False)

    pre_work_hours = fields.Float(string='Pre-Work Hours', compute='_compute_pre_core_post_work_hours_actual_tuned_break_hours', store=True, readonly=True)
    post_work_hours = fields.Float(string='Post-Work Hours', compute='_compute_pre_core_post_work_hours_actual_tuned_break_hours', store=True, readonly=True)
    core_work_hours = fields.Float(string='Core Work Hours', compute='_compute_pre_core_post_work_hours_actual_tuned_break_hours', store=True, readonly=True)

    overtime = fields.Float(string='Overtime', compute='_compute_overtime_undertime', store=True, readonly=True)
    undertime = fields.Float(string='Undertime', compute='_compute_overtime_undertime', store=True, readonly=True)
    lateness = fields.Float(string='Lateness', compute='_compute_lateness_earliness_over_breaking', store=True, readonly=True)
    earliness = fields.Float(string='Earliness', compute='_compute_lateness_earliness_over_breaking', store=True, readonly=True)
    over_breaking = fields.Float(string='Over-Breaking', compute='_compute_lateness_earliness_over_breaking', store=True, readonly=True)

    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], 'Day of Week', compute="_compute_dayofweek", store=True)
    include_pre_work = fields.Boolean('Include Pre-Work Hours', default=False)

    @api.depends('overtime', 'undertime')
    def compute_total_overtime_undertime(self):
        for record in self:
            record.total_overtime_undertime = record.overtime - record.undertime

    @api.depends('attendance_ids')
    def _compute_closed_attendance_ids(self):
        for rec in self:
            rec.closed_attendance_ids = rec.attendance_ids.filtered(lambda a: a.check_in and a.check_out)

    @api.depends('attendance_ids')
    def _compute_attendance_type(self):
        for rec in self:
            rec.attendance_type = 'present' if rec.attendance_ids else 'absent'

    @api.depends('planned_start_dt', 'planned_end_dt', 'planned_work_hours')
    def _compute_planned_break_hours(self):
        for rec in self:
            if rec.planned_start_dt and rec.planned_end_dt:
                rec.planned_break_hours = ((rec.planned_end_dt - rec.planned_start_dt).total_seconds() / 3600.0) - rec.planned_work_hours
            else:
                rec.planned_break_hours = 0

    @api.depends('attendance_ids')
    def _compute_actual_start_end_dt(self):
        for rec in self:
            actual_start_dt = False
            actual_end_dt = False

            employee_punches = set()
            for attendance_id in rec.attendance_ids:
                employee_punches.add(attendance_id.check_in)
                employee_punches.add(attendance_id.check_out)

            # Make sure to remove the False value in case any of the attendances above was not closed
            if False in employee_punches:
                employee_punches.remove(False)

            employee_punches = sorted(employee_punches)
            if employee_punches:
                actual_start_dt = employee_punches[0]
                actual_end_dt = employee_punches[-1]

            rec.actual_start_dt = actual_start_dt
            rec.actual_end_dt = actual_end_dt

    @api.depends('closed_attendance_ids')
    def _compute_actual_work_hours(self):
        for rec in self:
            rec.actual_work_hours = sum(attendance_id.worked_hours for attendance_id in rec.closed_attendance_ids)
            rec.actual_work_hours = round(rec.actual_work_hours, 2)

    @api.depends('planned_start_dt', 'planned_end_dt', 'actual_start_dt', 'actual_end_dt')
    def _compute_tuned_start_end_dt(self):
        for rec in self:
            company_threshold = rec.employee_id.company_id.overtime_company_threshold / 60.0
            employee_threshold = rec.employee_id.company_id.overtime_employee_threshold / 60.0
            rec.tuned_start_dt = False
            rec.tuned_end_dt = False

            if rec.actual_start_dt:
                start_dt = rec.planned_start_dt if rec.planned_start_dt else rec.actual_start_dt
                # consider rec.tuned_start_dt as start_dt if within threshold
                # if delta_in < 0: Checked in after supposed start of the day
                # if delta_in > 0: Checked in before supposed start of the day
                rec.tuned_start_dt = rec.actual_start_dt
                delta_in = (start_dt - rec.tuned_start_dt).total_seconds() / 3600.0
                if (0 < delta_in <= company_threshold) or (delta_in < 0 and abs(delta_in) <= employee_threshold):
                    # Started before or after planned date within the threshold interval
                    rec.tuned_start_dt = start_dt

            if rec.actual_end_dt:
                end_dt = rec.planned_end_dt if rec.planned_end_dt else rec.actual_end_dt
                # consider rec.tuned_end_dt as end_dt if within threshold
                # if delta_out < 0: Checked out before supposed end of the day
                # if delta_out > 0: Checked out after supposed end of the day
                rec.tuned_end_dt = rec.actual_end_dt
                delta_out = (rec.tuned_end_dt - end_dt).total_seconds() / 3600.0
                if (0 < delta_out <= company_threshold) or (delta_out < 0 and abs(delta_out) <= employee_threshold):
                    # Finished before or after planned date within the threshold interval
                    rec.tuned_end_dt = end_dt

    @api.depends('core_work_hours', 'overtime')
    def _compute_tuned_work_hours(self):
        for rec in self:
            rec.tuned_work_hours = rec.core_work_hours + rec.overtime

    @api.depends('planned_work_hours', 'tuned_break_hours', 'pre_work_hours', 'post_work_hours', 'lateness', 'earliness','include_pre_work')
    def _compute_overtime_undertime(self):
        for rec in self:
            if rec.planned_work_hours:
                if rec.include_pre_work:
                    rec.overtime = rec.pre_work_hours + rec.post_work_hours
                    rec.undertime = rec.planned_work_hours if rec.attendance_type == 'absent' else rec.lateness + rec.earliness

                else:
                    rec.overtime = rec.post_work_hours
                    rec.undertime = rec.planned_work_hours if rec.attendance_type == 'absent' else rec.lateness + rec.earliness
            else:
                # If no planned work hours, then all working hours are overtime, and no undertime
                rec.overtime = rec.actual_work_hours
                rec.undertime = 0

            # Round values
            rec.overtime = round(rec.overtime, 2)
            rec.undertime = round(rec.undertime, 2)

    @api.depends('tuned_start_dt', 'tuned_end_dt', 'tuned_break_hours')
    def _compute_lateness_earliness_over_breaking(self):
        for rec in self:
            start_dt = rec.planned_start_dt if rec.planned_start_dt else rec.actual_start_dt
            end_dt = rec.planned_end_dt if rec.planned_end_dt else rec.actual_end_dt

            # Ensure datetime fields are not None and are of correct type
            if isinstance(rec.tuned_start_dt, datetime) and isinstance(start_dt, datetime):
                delta_in = (rec.tuned_start_dt - start_dt).total_seconds() / 3600.0
                rec.lateness = delta_in if delta_in > 0 else 0
            else:
                rec.lateness = 0

            if isinstance(rec.tuned_end_dt, datetime) and isinstance(end_dt, datetime):
                delta_out = (end_dt - rec.tuned_end_dt).total_seconds() / 3600.0
                rec.earliness = delta_out if delta_out > 0 else 0
            else:
                rec.earliness = 0

            if rec.tuned_break_hours is not None and rec.planned_break_hours is not None:
                delta_break = rec.tuned_break_hours - rec.planned_break_hours
                rec.over_breaking = delta_break if (delta_break > 0 and rec.planned_work_hours) else 0
            else:
                rec.over_breaking = 0

            # Round values
            rec.lateness = round(rec.lateness, 2)
            rec.earliness = round(rec.earliness, 2)
            rec.over_breaking = round(rec.over_breaking, 2)

    @api.depends('actual_start_dt', 'actual_end_dt', 'planned_break_hours')
    def _compute_pre_core_post_work_hours_actual_tuned_break_hours(self):
        for rec in self:
            company_threshold = rec.employee_id.company_id.overtime_company_threshold / 60.0
            employee_threshold = rec.employee_id.company_id.overtime_employee_threshold / 60.0
            start_dt = rec.planned_start_dt if rec.planned_start_dt else rec.actual_start_dt
            end_dt = rec.planned_end_dt if rec.planned_end_dt else rec.actual_end_dt

            rec.pre_work_hours = 0
            rec.core_work_hours = 0
            rec.post_work_hours = 0
            rec.actual_break_hours = 0
            next_utc_check_in = False

            for attendance_id in rec.closed_attendance_ids:
                # consider check_in as start_dt if within threshold
                # if delta_in < 0: Checked in after supposed start of the day
                # if delta_in > 0: Checked in before supposed start of the day
                utc_check_in = attendance_id.check_in
                delta_in = (start_dt - utc_check_in).total_seconds() / 3600.0
                if (0 < delta_in <= company_threshold) or (delta_in < 0 and abs(delta_in) <= employee_threshold):
                    # Started before or after planned date within the threshold interval
                    utc_check_in = start_dt

                # same for check_out as end_dt
                # if delta_out < 0: Checked out before supposed end of the day
                # if delta_out > 0: Checked out after supposed end of the day
                utc_check_out = attendance_id.check_out
                delta_out = (utc_check_out - end_dt).total_seconds() / 3600.0
                if (0 < delta_out <= company_threshold) or (delta_out < 0 and abs(delta_out) <= employee_threshold):
                    # Finished before or after planned date within the threshold interval
                    utc_check_out = end_dt

                # There is an overtime at the start of the day
                if utc_check_in < start_dt:
                    rec.pre_work_hours += (min(start_dt, utc_check_out) - utc_check_in).total_seconds() / 3600.0
                # Interval inside the working hours -> Considered as working time
                if utc_check_in <= end_dt and utc_check_out >= start_dt:
                    rec.core_work_hours += (min(end_dt, utc_check_out) - max(start_dt, utc_check_in)).total_seconds() / 3600.0
                # There is an overtime at the end of the day
                if utc_check_out > end_dt:
                    rec.post_work_hours += (utc_check_out - max(end_dt, utc_check_in)).total_seconds() / 3600.0

                # Compute actual_break_hours if there is breaking within the working hours
                if next_utc_check_in and utc_check_out > start_dt and next_utc_check_in < end_dt:
                    rec.actual_break_hours += (next_utc_check_in - utc_check_out).total_seconds() / 3600.0
                next_utc_check_in = utc_check_in

            # consider rec.tuned_break_hours as rec.planned_break_hours if less than rec.planned_break_hours or within employee_threshold
            # if delta_break > 0: Total break less than planned
            # if delta_break < 0: Total break more than planned
            rec.tuned_break_hours = rec.actual_break_hours
            delta_break = (rec.planned_break_hours - rec.tuned_break_hours)
            if delta_break > 0:
                rec.core_work_hours -= delta_break
                rec.tuned_break_hours = rec.planned_break_hours
            elif delta_break < 0 and (abs(delta_break) <= employee_threshold):
                rec.core_work_hours += abs(delta_break)
                rec.tuned_break_hours = rec.planned_break_hours

            # Core_work_hours min value should be '0'
            # If no planned_work_hours, whole work time is overtime, therefore core_work_hours should be '0'
            if rec.core_work_hours < 0 or not rec.planned_work_hours:
                rec.core_work_hours = 0

            # Round values
            rec.pre_work_hours = round(rec.pre_work_hours, 2)
            rec.core_work_hours = round(rec.core_work_hours, 2)
            rec.post_work_hours = round(rec.post_work_hours, 2)
            rec.actual_break_hours = round(rec.actual_break_hours, 2)
            rec.tuned_break_hours = round(rec.tuned_break_hours, 2)

    @api.depends('attendance_date')
    def _compute_dayofweek(self):
        for rec in self:
            rec.dayofweek = str(rec.attendance_date.weekday())

    # def action_validate(self):
    #     for rec in self:
    #         rec.state = 'validated'
    #         date_start = rec.attendance_date.replace(day=1)
    #         last_day = calendar.monthrange(rec.attendance_date.year, rec.attendance_date.month)[1]
    #         date_end = rec.attendance_date.replace(day=last_day)
    #
    #         work_entry_regeneration_wizard_id = self.env['hr.work.entry.regeneration.wizard'].create({
    #             'date_from': date_start,
    #             'date_to': date_end,
    #             'employee_ids': [fields.Command.set([rec.employee_id.id])],
    #         })
    #         work_entry_regeneration_wizard_id.regenerate_work_entries()
    #
    # def action_cancel(self):
    #     for rec in self:
    #         rec.state = 'cancelled'
    #
    # def action_draft(self):
    #     for rec in self:
    #         rec.state = 'draft'

    def synchronize_daily_attendance_for(self, employee_id, daily_attendance_date):
        assert employee_id is not None
        assert isinstance(daily_attendance_date, date)

        # As _attendance_intervals_batch and _leave_intervals_batch both take localized dates we need to localize those dates
        daily_attendance_datetime = datetime.combine(daily_attendance_date, datetime.min.time())
        employee_timezone = pytz.timezone(employee_id.tz or 'UTC')
        emp_tz_start = employee_timezone.localize(daily_attendance_datetime.replace(hour=0, minute=0, second=0))
        emp_tz_end = employee_timezone.localize(daily_attendance_datetime.replace(hour=23, minute=59, second=59))
        emp_utc_start = emp_tz_start.astimezone(pytz.utc)
        emp_utc_end = emp_tz_end.astimezone(pytz.utc)
        daily_attendance_record = self.search([
            ('employee_id', '=', employee_id.id),
            ('attendance_date', '=', daily_attendance_date)
        ], limit=1)

        expected_attendances = employee_id.resource_calendar_id._attendance_intervals_batch(
            emp_utc_start, emp_utc_end, employee_id.resource_id
        )[employee_id.resource_id.id]

        # Subtract Global Leaves and Employee's Leaves
        hr_attendance = self.env['hr.attendance']
        leave_intervals = employee_id.resource_calendar_id._leave_intervals_batch(
            emp_utc_start, emp_utc_end, employee_id.resource_id,
            domain=hr_attendance._get_overtime_leave_domain()
        )
        expected_attendances -= leave_intervals[False] | leave_intervals[employee_id.resource_id.id]
        working_times = defaultdict(lambda: [])
        for expected_attendance in expected_attendances:
            working_times[expected_attendance[0].date()].append(expected_attendance[:3])

        work_entry_type_id = False
        planned_start_dt, planned_end_dt = False, False
        planned_work_hours = 0

        if working_times:
            work_entry_type_id = self.env.ref('erpc_daily_attendance.erpc_hr_work_entry_type_working_hours')
            for calendar_attendance in working_times[daily_attendance_date]:
                planned_start_dt = min(planned_start_dt, calendar_attendance[0]) if planned_start_dt else calendar_attendance[0]
                planned_end_dt = max(planned_end_dt, calendar_attendance[1]) if planned_end_dt else calendar_attendance[1]
                planned_work_hours += (calendar_attendance[1] - calendar_attendance[0]).total_seconds() / 3600.0

        if not daily_attendance_record:
            daily_attendance_record = self.create({
                'employee_id': employee_id.id,
                'attendance_date': daily_attendance_date,
                'attendance_date_start': emp_utc_start.replace(tzinfo=None),
                'attendance_date_end': emp_utc_end.replace(tzinfo=None),
                'work_entry_type_id': work_entry_type_id.id if work_entry_type_id else False,
                'planned_start_dt': planned_start_dt.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S") if planned_start_dt else False,
                'planned_end_dt': planned_end_dt.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S") if planned_end_dt else False,
                'planned_work_hours': planned_work_hours,
            })

        daily_attendance_record._synchronize_daily_attendance(
            emp_utc_start,
            emp_utc_end,
            work_entry_type_id,
            planned_start_dt,
            planned_end_dt,
            planned_work_hours
        )

    def _synchronize_daily_attendance(self, emp_utc_start, emp_utc_end, work_entry_type_id, planned_start_dt, planned_end_dt, planned_work_hours):
        self.ensure_one()
        _log.info(f'\n\n_synchronize_daily_attendance: for {self.employee_id.name} ({self.employee_id.id}) between {self.attendance_date_start} and {self.attendance_date_end}\n\n\n')

        # Update the passed values
        self.work_entry_type_id = work_entry_type_id.id if work_entry_type_id else False
        self.planned_start_dt = planned_start_dt.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S") if planned_start_dt else False
        self.planned_end_dt = planned_end_dt.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S") if planned_end_dt else False
        self.planned_work_hours = planned_work_hours

        # Check for attendances
        attendance_ids = self.env['hr.attendance'].search([
            ('employee_id', '=', self.employee_id.id),
            ('check_in', '>=', self.attendance_date_start),
            ('check_in', '<=', self.attendance_date_end),
            '|',
            ('check_out', '<=', self.attendance_date_end),
            ('check_out', '=', False),
        ])

        daily_attendance_line_ids = []
        for attendance_id in attendance_ids:
            daily_attendance_line_id = self.env['erpc.hr.daily.attendance.line'].create({
                'daily_attendance_id': self.id,
                'attendance_id': attendance_id.id,
            })
            daily_attendance_line_ids.append(daily_attendance_line_id.id)
        self.attendance_ids = [fields.Command.set(daily_attendance_line_ids)]

        # Check for leaves last and if there is any, update the work_entry_type_id
        all_leaves = self.env['resource.calendar.leaves'].search([
            ('resource_id', '=', self.employee_id.resource_id.id),
            ('date_to', '>=', emp_utc_start.replace(tzinfo=None)),
            ('date_from', '<=', emp_utc_end.replace(tzinfo=None)),
        ])
        if all_leaves:
            leave_work_entry_type_ids = all_leaves.mapped('work_entry_type_id')
            self.work_entry_type_id = leave_work_entry_type_ids[0] if leave_work_entry_type_ids else False
