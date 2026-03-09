from odoo import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Entry Created'),
        ('paid', 'Paid'),
        ('cancel', 'Rejected')],
        string='Status', index=True, readonly=True, copy=False,
        default='draft', tracking=True,
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Entry Created\'.
                \n* When user cancel payslip the status is \'Rejected\'.""")
