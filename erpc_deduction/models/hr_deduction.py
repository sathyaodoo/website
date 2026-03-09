from odoo import models, fields, api, _


class HrDeduction(models.Model):
    _name = 'hr.deduction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Deduction"

    name = fields.Char(string="Deduction Name", default="/", readonly=True, help="Name of the deduction")
    date = fields.Date(string="Date", default=fields.Date.today(), help="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee")
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True, string="Department", help="Employee")
    company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company", default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency", default=lambda self: self.env.user.company_id.currency_id, readonly=True)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position", help="Job position")
    deduction_amount = fields.Float(string="Deduction Amount", required=True, help="Deduction amount")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")
    paid = fields.Boolean(string="Paid", readonly=True)
    note = fields.Text(string="Description")

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('hr.deduction.seq') or ' '
        res = super(HrDeduction, self).create(values)
        return res


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_deduction(self):
        self.deduction_count = self.env['hr.deduction'].search_count([('employee_id', '=', self.id)])

    deduction_count = fields.Integer(string="Deduction Count", compute='_compute_employee_deduction')
