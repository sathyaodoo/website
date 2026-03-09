from odoo import api, fields, models


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    # lives_in_yokohama = fields.Boolean('Lives in Yokohama',
    #                                    help="When this field is checked the employee is eligible for Sunday Leaves",)
