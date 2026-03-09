from odoo import models, fields, api, _
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class EmployeeExpirationNotification(models.Model):
    _inherit = 'hr.employee'

    def check_expiration_dates(self):
        today = fields.Date.context_today(self)
        reminder_date = today + timedelta(days=30)

        employees = self.env['hr.employee'].search([
            '|',
            ('visa_expire', '=', reminder_date),
            ('work_permit_expiration_date', '=', reminder_date),
        ])

        for employee in employees:
            if not employee.user_id:
                _logger.warning(f"Employee {employee.name} does not have an associated user. Assigning default user.")
                # Assign a default user, e.g., system admin (user with ID 1)
                default_user_id = self.env.ref('base.user_admin').id
            else:
                default_user_id = employee.user_id.id

            # Determine activity summary and note
            summary = _("Document Expiration Reminder")
            note = _(
                f"Dear {employee.name},<br/><br/>"
                f"The following documents are about to expire:<br/>"
                f"<ul>"
                f"<li><strong>Visa Expiration Date:</strong> {employee.visa_expire or 'N/A'}</li>"
                f"<li><strong>Work Permit Expiration Date:</strong> {employee.work_permit_expiration_date or 'N/A'}</li>"
                f"</ul>"
                f"Please take the necessary action."
            )

            # Create an activity for the employee's related user
            activity_values = {
                'res_model_id': self.env['ir.model']._get_id('hr.employee'),
                'res_id': employee.id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_email').id,
                'summary': summary,
                'note': note,
                'user_id': default_user_id,
                'date_deadline': reminder_date,
            }

            self.env['mail.activity'].create(activity_values)
