from odoo import api, fields, models


class HRAttendanceReminder(models.Model):
    _name = 'hr.attendance.reminder'

    employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True)
    reminder_type = fields.Selection([
        ('check_in', 'Check-In'),
        ('check_out', 'Check-Out'),
        ('timeoff', 'Time-Off'),
    ], string="Type", readonly=True)
    date = fields.Date(string="Date", readonly=True)
    processed = fields.Boolean(string="Processed")
    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], 'Day of Week', compute="_compute_dayofweek", store=True)

    @api.depends('date')
    def _compute_dayofweek(self):
        for rec in self:
            rec.dayofweek = str(rec.date.weekday())

    def action_create_time_off(self):
        self.ensure_one()
        self.processed = True
        action = self.env["ir.actions.actions"]._for_xml_id("hr_holidays.hr_leave_action_action_approve_department")
        action['views'] = [(False, 'form')]
        action['context'] = {
            'search_default_waiting_for_me': 1,
            'search_default_waiting_for_me_manager': 2,
            'hide_employee_name': 1,
            'holiday_status_display_name': False,
            'default_employee_ids': [self.employee_id.id]
        }
        return action

    def action_dismiss(self):
        for rec in self:
            rec.processed = True

    def update_hr_attendance_reminder_data_all(self):
        self.check_in_reminder()
        self.check_out_reminder()

    def update_hr_attendance_reminder_data_for(self, reminder_type, employee_id, date):
        old_reminders = self.env['hr.attendance.reminder'].search([
            ('employee_id', '=', employee_id.id),
            ('reminder_type', '=', reminder_type),
            ('date', '=', date),
        ])
        if old_reminders:
            old_reminders.unlink()

        self.env['hr.attendance.reminder'].create({
            'employee_id': employee_id.id,
            'reminder_type': reminder_type,
            'date': date,
        })

    def check_timeoff_reminder(self):
        # Get active employees
        employees = self.env['hr.employee'].search([('active', '=', True), ('send_attendance_reminder', '=', True)])

        # Collect names of employees who are off today
        employee_names = []
        for employee_id in employees:
            today = fields.Date.today()
            if employee_id.has_time_off_today():
                self.update_hr_attendance_reminder_data_for('timeoff', employee_id, today)
                employee_names.append(employee_id.name)

        return employee_names

    def check_in_reminder(self):
        # Get active employees
        employees = self.env['hr.employee'].search([('active', '=', True), ('send_attendance_reminder', '=', True)])

        # Collect names of employees who haven't checked in today and are not off today
        employee_names = []
        for employee_id in employees:
            # Variables needed
            today = fields.Date.today()
            today_dayofweek = str(today.weekday())

            # By default, we suppose that the employee is not working today,
            # then we update the value base on the working schedule
            employee_is_working_today = False
            resource_calendar_id = employee_id.resource_calendar_id
            if resource_calendar_id:
                working_schedule_days_of_week = resource_calendar_id.attendance_ids.mapped('dayofweek')
                if today_dayofweek in working_schedule_days_of_week:
                    employee_is_working_today = True

            # Time off should be checked only if employee is actually working today
            if employee_is_working_today:
                employee_is_working_today = not employee_id.has_time_off_today()

            # Final Check
            if employee_is_working_today and not employee_id.check_in_today():
                self.update_hr_attendance_reminder_data_for('check_in', employee_id, today)
                employee_names.append(employee_id.name)

        return employee_names

    def check_out_reminder(self):
        # Get active employees who are included in attendance reminder
        employees = self.env['hr.employee'].search([('active', '=', True), ('send_attendance_reminder', '=', True)])

        # Collect names of employees who haven't checked out today and are not off today
        employee_names = []
        for employee_id in employees:
            # Variables needed
            today = fields.Date.today()
            today_dayofweek = str(today.weekday())

            # By default, we suppose that the employee is not working today,
            # then we update the value base on the working schedule
            employee_is_working_today = False
            resource_calendar_id = employee_id.resource_calendar_id
            if resource_calendar_id:
                working_schedule_days_of_week = resource_calendar_id.attendance_ids.mapped('dayofweek')
                if today_dayofweek in working_schedule_days_of_week:
                    employee_is_working_today = True

            # Time off should be checked only if employee is actually working today
            if employee_is_working_today:
                employee_is_working_today = not employee_id.has_time_off_today()

            # Final Check
            if employee_is_working_today and not employee_id.check_out_today():
                self.update_hr_attendance_reminder_data_for('check_out', employee_id, today)
                employee_names.append(employee_id.name)

        return employee_names

    @api.model
    def send_email_to_hr(self, hr_email, employee_names, reminder_type):
        if reminder_type == 'check_in':
            subject = "Employee Check-in Reminder"
            body = f"<div><p>The following employees have not checked in yet today:</p></div>"
        elif reminder_type == 'check_out':
            subject = "Employee Check-out Reminder"
            body = f"<div><p>The following employees have not checked out yet today:</p></div>"
        elif reminder_type == 'timeoff':
            subject = "Employee Time-Off Reminder"
            body = f"<div><p>The following employees are off today:</p></div>"

        body += "".join(f"<div><p>{employee_name}</p></div>" for employee_name in employee_names)

        # Send email to HR
        mail_values = {
            'email_from': self.env.user.email,
            'email_to': hr_email,
            'subject': subject,
            'body_html': body,
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()

    @api.model
    def send_timeoff_reminder(self):
        # Send email to HR if there are employees who are off
        hr_manager_email = 'hr@yokohamalebanon.com, marwan@yokohamalebanon.com'  # Replace with HR email
        employee_names = self.check_timeoff_reminder()
        if employee_names:
            self.send_email_to_hr(hr_manager_email, employee_names, 'timeoff')

    @api.model
    def send_check_in_reminder(self):
        # Make sure to get the latest attendances before proceeding
        machine_ids = self.env['zk.machine'].search([])
        machine_ids.get_attendances()

        # Send email to HR if there are employees who haven't checked in
        hr_manager_email = 'hr@yokohamalebanon.com, marwan@yokohamalebanon.com'  # Replace with HR email
        employee_names = self.check_in_reminder()
        if employee_names:
            self.send_email_to_hr(hr_manager_email, employee_names, 'check_in')

    @api.model
    def send_check_out_reminder(self):
        # Make sure to get the latest attendances before proceeding
        machine_ids = self.env['zk.machine'].search([])
        machine_ids.get_attendances()

        # Send email to HR if there are employees who haven't checked out
        hr_manager_email = 'hr@yokohamalebanon.com, marwan@yokohamalebanon.com'  # Replace with HR email
        employee_names = self.check_out_reminder()
        if employee_names:
            self.send_email_to_hr(hr_manager_email, employee_names, 'check_out')
