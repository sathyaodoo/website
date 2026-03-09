from odoo import models, fields, api, _


class HrAddittionalAllowances(models.Model):
    _name = 'hr.additional.allowances'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Additional Allowances"

    name = fields.Char(string="Additional Allowance Name", default="/", readonly=True,
                       help="Name of the Additional Allowance")
    date = fields.Date(string="Date", default=fields.Date.today(), help="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee")
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Department", help="Employee")
    company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id, readonly=True)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position",
                                   help="Job position")
    add_allowances_amount = fields.Float(string="Additional Allowance Amount", required=True,
                                         help="Additional Allowance amount")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")
    batch_id = fields.Many2one('hr.payslip.run', string="Payslip Batch", help="Batch Reference")
    paid = fields.Boolean(string="Paid", readonly=True, copy=False)
    note = fields.Text(string="Notes")

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('hr.additional.allowances.seq') or ' '
        res = super(HrAddittionalAllowances, self).create(values)
        return res


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    add_allowances_count = fields.Integer(string="Additional Allowance Count", compute='_compute_employee_allowances')

    def _compute_employee_allowances(self):
        self.add_allowances_count = self.env['hr.additional.allowances'].search_count([('employee_id', '=', self.id)])
