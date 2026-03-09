from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from datetime import datetime, timedelta
from datetime import date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    resource_calendar_id = fields.Many2one(related='version_id.resource_calendar_id', inherited=True, index=False, store=False, check_company=True, readonly=True)
    job_id = fields.Many2one('hr.job', readonly=True)
    department_id = fields.Many2one('hr.department', readonly=True)
    #TODO: To add required
    is_working_spouse = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="Working Spouse",
                                       help="This field is checked if the partner is a working partner")
    #TODO: To uncomment
    # is_working_spouse = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="Working Spouse",
    #                                    help="This field is checked if the partner is a working partner", required=True)
    is_nssf_social_detection = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="NSSF Social Detection",
                                              help="If female and has dependent kids a social security detection declaration (تحقيق اجتماعي) should be checked to get family allowance", required=True, default='no')
    number_of_kids = fields.Integer(string="Number of Kids", help="Specify number of kids that the employee has")
    #TODO: To add required
    has_establishment = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="Has Establishment", help="This field specifies if an employee has his own establishment")
    #TODO: To uncomment
    # has_establishment = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="Has Establishment", help="This field specifies if an employee has his own establishment", required=True)
    employee_age = fields.Integer(string="Age", compute="_compute_employee_age", store=True)

    @api.depends('birthday')
    def _compute_employee_age(self):
        today = date.today()
        for employee in self:
            if employee.birthday:
                employee.employee_age = today.year - employee.birthday.year - (
                        (today.month, today.day) < (employee.birthday.month, employee.birthday.day)
                )
            else:
                employee.employee_age = 0
