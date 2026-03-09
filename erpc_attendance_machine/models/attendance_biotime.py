import pytz
from datetime import time, datetime
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class AttendanceBioTime(models.Model):
    _name = 'attendance.biotime'
    _description = 'Attendance BioTime Machine'
    _order = "datetime ,id"

    id_employee_device = fields.Char(string='Employee ID', help="The ID of the employee in the biotime machine")
    employee_id = fields.Many2one('hr.employee', string='Employee', compute='_compute_employee_id', store=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True, related="employee_id.company_id")
    employee_name = fields.Char(string='Employee Name')
    department = fields.Char(string='Department')
    date = fields.Date(string='Date')
    str_time = fields.Char(string='Time')
    datetime = fields.Datetime(string='Date Time', compute='_compute_check_date_time', store=True)
    punch_state = fields.Selection([
        ('Check In', 'Check In'),
        ('Check Out', 'Check Out'),
    ], string='Punching Type')
    data_src = fields.Selection([
        ('Device', 'Device'),
        ('Mobile', 'Mobile'),
    ], string='Data Source')
    import_state = fields.Selection([('pending', "Pending"), ('imported', "Imported"), ('skipped', "Skipped")], string="Import State", default="pending")
    import_error = fields.Text("Import Error", readonly=True)

    @api.depends('id_employee_device')
    def _compute_employee_id(self):
        for record in self:
            if record.id_employee_device:
                employee = self.env['hr.employee'].search([('device_id', '=', record.id_employee_device)], limit=1)
                record.employee_id = employee.id if employee else False
            else:
                record.employee_id = False

    @api.depends('date', 'str_time')
    def _compute_check_date_time(self):
        for record in self:
            record.datetime = False
            if record.date and record.str_time:
                hours = int(record.str_time[-8:-6])
                minutes = int(record.str_time[-5:-3])
                seconds = int(record.str_time[-2:])
                new_datetime = datetime.combine(record.date, time(hours, minutes, seconds))
                utz = pytz.timezone(self.env.user.tz)
                datetime_utz = utz.localize(new_datetime)
                datetime_utc = datetime_utz.astimezone(pytz.utc)
                record.datetime = datetime_utc.replace(tzinfo=None)

    def create_biotime_attendance(self):
        # Get the pending attendances sorted by datetime asc
        pending_attendance_ids = self.filtered(lambda attendance: attendance.import_state == 'pending')
        pending_attendance_ids = pending_attendance_ids.sorted(key='datetime')
        _logger.info(f'\nERPC:\n**PENDING ATTENDANCES**:\t{pending_attendance_ids}\n.')

        for pending_attendance_id in pending_attendance_ids:
            # Make sure that employee_id is defined
            if not pending_attendance_id.employee_id:
                pending_attendance_id.import_error = "employee_id is not defined"
                pending_attendance_id.import_state = 'skipped'
                _logger.warning(f'\nERPC:\n**ATTENDANCE SKIPPED**:\t{pending_attendance_id} import_error: {pending_attendance_id.import_error}\n.')
                continue

            # Get the last_attendance_id for this employee
            last_attendance_id = self.env['hr.attendance'].sudo().search([('employee_id', '=', pending_attendance_id.employee_id.id)], order='check_in desc', limit=1)

            # Case 1: No previous attendances => Create first attendance for this employee
            if not last_attendance_id:
                _logger.info(f'\nERPC:\n**CASE 1**:\tNo previous attendances for {pending_attendance_id.employee_id.name}\n.')
                self.env['hr.attendance'].sudo().create({
                    'employee_id': pending_attendance_id.employee_id.id,
                    'check_in': pending_attendance_id.datetime,
                })
                pending_attendance_id.import_state = 'imported'
                _logger.info(f'\nERPC:\n**ATTENDANCE IMPORTED**:\t{pending_attendance_id} for {pending_attendance_id.employee_id.name} on: {pending_attendance_id.datetime}\n.')
                continue

            # Case 2: There are some previous attendances
            _logger.info(f'\nERPC:\n**CASE 2**:\tThere are some previous attendances for {pending_attendance_id.employee_id.name}\n.')

            # Make sure that there are no open attendances for the employee at any date, as this prevent us from creating any new attendance
            open_attendance_ids = self.env['hr.attendance'].sudo().search([
                ('employee_id', '=', pending_attendance_id.employee_id.id),
                ('check_out', '=', False),
            ])
            for open_attendance_id in open_attendance_ids:
                _logger.info(f'\nERPC:\n**AUTO CLOSING ATTENDANCE**:\topen_attendance_id {open_attendance_id} is auto closed with check_out = {open_attendance_id.check_in}\n.')
                open_attendance_id.sudo().update({
                    'check_out': open_attendance_id.check_in,
                })

            # Get the date without time for both pending_attendance_id.datetime and last_attendance_id.check_in to compare them (in employee's timezone)
            employee_timezone = pytz.timezone(pending_attendance_id.employee_id.tz)
            pending_attendance_datetime_utc = pytz.utc.localize(pending_attendance_id.datetime)
            pending_attendance_datetime_etz = pending_attendance_datetime_utc.astimezone(employee_timezone)
            pending_attendance_day_utc = pending_attendance_datetime_utc.date()
            pending_attendance_day_etz = pending_attendance_datetime_etz.date()

            last_attendance_datetime_utc = pytz.utc.localize(last_attendance_id.check_in)
            last_attendance_datetime_etz = last_attendance_datetime_utc.astimezone(employee_timezone)
            last_attendance_day_utc = last_attendance_datetime_utc.date()
            last_attendance_day_etz = last_attendance_datetime_etz.date()

            _logger.info(f'\nERPC:\n**PYTZ ATTENDANCES**:\t UTC attendance for the employee {pending_attendance_datetime_utc} and {last_attendance_datetime_utc}\n.')
            _logger.info(f'\nERPC:\n**EMPLOYEE TIMEZONE ATTENDANCES**:\t ETZ attendance for the employee  {pending_attendance_datetime_etz} and {last_attendance_datetime_etz}\n.')

            # Case 2.1: The pending_attendance_day_etz is after the last_attendance_day_etz
            if pending_attendance_day_etz > last_attendance_day_etz:
                _logger.info(f'\nERPC:\n**CASE 2.1**:\tThe pending_attendance_day_etz ({pending_attendance_day_etz}) is after the last_attendance_day_etz ({last_attendance_day_etz}) \n.')

                # Create new attendance for the employee
                self.env['hr.attendance'].sudo().create({
                    'employee_id': pending_attendance_id.employee_id.id,
                    'check_in': pending_attendance_id.datetime,
                })
                pending_attendance_id.import_state = 'imported'
                _logger.info(f'\nERPC:\n**ATTENDANCE IMPORTED**:\t{pending_attendance_id} for {pending_attendance_id.employee_id.name} on: {pending_attendance_id.datetime}\n.')
                continue

            # If you are here, then the pending_attendance_day_etz is either equal to the last_attendance_day_etz or before it
            # => Get all the attendances of the employee in the day of the pending_attendance_day_utc (sorted check_in asc)
            # TODO: Need to double check if it is actually getting the right attendances of the employee
            #  in the right date incase the timezone difference was big
            pending_attendance_day_start_utc = datetime.combine(pending_attendance_day_utc, time(0, 0, 0))
            pending_attendance_day_end_utc = datetime.combine(pending_attendance_day_utc, time(23, 59, 59))

            employee_attendance_ids = self.env['hr.attendance'].sudo().search([
                ('employee_id', '=', pending_attendance_id.employee_id.id),
                ('check_in', '>=', pending_attendance_day_start_utc),
                ('check_in', '<=', pending_attendance_day_end_utc),
            ], order='check_in asc')
            _logger.info(f'\nERPC:\n**EMPLOYEE PREVIOUS ATTENDANCES**:\t Previous attendance for the employee between UTC: {pending_attendance_day_start_utc} and {pending_attendance_day_end_utc}:\n{employee_attendance_ids}\n.')

            # Collect the punches of employee in the set employee_punches which will then
            # be converted to a list of unique punches for the employee at that day
            employee_punches = set()
            for employee_attendance_id in employee_attendance_ids:
                employee_punches.add(employee_attendance_id.check_in)
                employee_punches.add(employee_attendance_id.check_out)

            # Make sure that the set does not contain a False value
            if False in employee_punches:
                employee_punches.remove(False)

            # Add the punch the current pending_attendance_id to the employee_punches set, then convert it to sorted list of punches
            employee_punches.add(pending_attendance_id.datetime)
            employee_punches = sorted(employee_punches)
            _logger.info(f'\nERPC:\n**EMPLOYEE COLLECTED PUNCHES**:\t The collected punches for the employee between UTC: {pending_attendance_day_start_utc} and {pending_attendance_day_start_utc}:\n{employee_punches}\n.')

            employee_attendance_ids.sudo().unlink()
            _logger.info(
                f'\nERPC:\n**PREVIOUS ATTENDANCES DELETED**:\t The previous attendances are successfully deleted for the employee between UTC: {pending_attendance_day_start_utc} and {pending_attendance_day_start_utc}\n{employee_attendance_ids}\n.')

            # There are two approaches here:
            #   1st approach: Loop over the employee_punches and for each one either create a new attendance or close the previous one respectively
            #      Commented for now cz the client wants the 2nd approach
            # last_created_attendance_id = False
            # for employee_punch in employee_punches:
            #     if not last_created_attendance_id:
            #         last_created_attendance_id = self.env['hr.attendance'].sudo().create({
            #             'employee_id': pending_attendance_id.employee_id.id,
            #             'check_in': employee_punch,
            #         })
            #     else:
            #         last_created_attendance_id.sudo().update({
            #             'check_out': employee_punch,
            #         })
            #         last_created_attendance_id = False
            # _logger.info(f'\nERPC:\n**NEW ATTENDANCES CREATED**:\t New attendances are successfully created for the employee between {pending_attendance_day_start_utc} and {pending_attendance_day_end_utc}\n.')
            #
            # Case 2 Exception: If The pending_attendance_day_etz is before the last_attendance_day:
            # Check if last_created_attendance_id value exist which means that the last created attendance was not closed
            # In that case make sure to close it
            # if last_created_attendance_id and pending_attendance_day_etz < last_attendance_day_etz:
            #     _logger.info(f'\nERPC:\n**CASE 2 EXCEPTION**:\tThe pending_attendance_day_etz ({pending_attendance_day_etz}) is before the last_attendance_day_etz ({last_attendance_day_etz})\n.')
            #     _logger.info(f'\nERPC:\n**AUTO CLOSING ATTENDANCE**:\tlast_created_attendance_id {last_created_attendance_id} is auto closed with check_out = {last_created_attendance_id.check_in} (UTC)\n.')
            #     last_created_attendance_id.sudo().update({
            #         'check_out': last_created_attendance_id.check_in,
            #     })
            #
            #   2nd approach: Get only the first and last punches and create a single attendance record for the employee
            #       In case there was only once single punch in the list, employee_punches[0] and employee_punches[-1] will be referencing same value,
            #       thus the attendance will still close itself.

            checkin = employee_punches[0]
            checkout = employee_punches[-1]
            self.env['hr.attendance'].sudo().create({
                'employee_id': pending_attendance_id.employee_id.id,
                'check_in': checkin,
                'check_out': checkout,
            })
            pending_attendance_id.import_state = 'imported'
