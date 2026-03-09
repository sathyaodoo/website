from odoo import api, models, fields, _

import logging

_logger = logging.getLogger(__name__)


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    device_id = fields.Char(string='Device ID', groups="hr.group_hr_user", help="Input the device ID to get the employee's attendance from the punch machine")
