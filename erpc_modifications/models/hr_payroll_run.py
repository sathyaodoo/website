from odoo import models, fields, api, _


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    state = fields.Selection([
        ('draft', 'New'),
        ('verify', 'Confirmed'),
        ('close', 'Entry Created'),
        ('paid', 'Paid'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft', store=True, compute='_compute_state_change')
