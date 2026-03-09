from odoo import api, models, fields, _

import logging

_logger = logging.getLogger(__name__)


class HREmployee(models.Model):
    _inherit = 'hr.attendance'

    attendance_offline_id = fields.Many2one('attendance.offline', string='Attendance Offline')
    checkin_equals_checkout = fields.Boolean(string="Checkin Equals Checkout", compute='_compute_checkin_equals_checkout', store=True)

    @api.depends('check_in', 'check_out')
    def _compute_checkin_equals_checkout(self):
        for employee in self:
            employee.checkin_equals_checkout = employee.check_in and employee.check_out and employee.check_in == employee.check_out
