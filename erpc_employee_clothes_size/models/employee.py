from odoo import models, fields, api, _
import logging

logger = logging.getLogger(__name__)


class Employee(models.Model):
    _inherit = "hr.employee"
    hourly_cost = fields.Monetary('Hourly Cost', compute='_compute_hourly_cost', currency_field='currency_id',
                                  groups="hr.group_hr_user", default=0.0)
    home_allowance = fields.Boolean(string='Home Allowance', help='If you check this checkbox a value of 20% from SMO will be calculated for the employee in payroll.')

    @api.depends('version_id.wage')
    def _compute_hourly_cost(self):
        monthly_hours_param = self.env['ir.config_parameter'].sudo().get_param('monthly_hours')
        if not monthly_hours_param:
            monthly_hours = None
        else:
            monthly_hours = float(monthly_hours_param)

        for employee in self:
            if employee.version_id and monthly_hours:
                monthly_wage = employee.version_id.wage
                employee.hourly_cost = monthly_wage / monthly_hours
            else:
                employee.hourly_cost = 0

    clothes_size = fields.Selection(
        selection=[
            ("", ""),
            ("s", "S"),
            ("m", "M"),
            ("l", "L"),
            ("xl", "XL"),
            ("xxl", "XXL"),
        ],
        string="Clothes Size",
        copy=False
    )
