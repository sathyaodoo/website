from odoo import models, fields, api, _


class HrCommission(models.Model):
    _name = 'hr.commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Commission / Target / Bonus"

    name = fields.Char(string="Commission / Target / Bonus Name", default="/", readonly=True, help="Name of the Commission / Target / Bonus")
    date = fields.Date(string="Date", default=fields.Date.today(), help="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee")
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True, string="Department", help="Employee")
    company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company", default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency", default=lambda self: self.env.user.company_id.currency_id, readonly=True)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position", help="Job position")
    commission_amount = fields.Float(string="Commission / Target / Bonus Amount", required=True, help="Commission / Target / Bonus amount")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")
    batch_id = fields.Many2one('hr.payslip.run', string="Payslip Batch", help="Batch Reference")
    paid = fields.Boolean(string="Paid", readonly=True, copy=False)
    note = fields.Text(string="Description")
    tires_qty = fields.Float(string="Tires Qty", digits=(16, 0))
    tires_values = fields.Float(string="Tires Values", digits=(16, 0))
    batteries_qty = fields.Float(string="Batteries Qty", digits=(16, 0))
    batteries_values = fields.Float(string="Batteries Values", digits=(16, 0))
    oil_qty = fields.Float(string="Oil Qty", digits=(16, 0))
    oil_values = fields.Float(string="Oil Values", digits=(16, 0))


    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('hr.commission.seq') or ' '
        res = super(HrCommission, self).create(values)
        return res


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_commission(self):
        self.commission_count = self.env['hr.commission'].search_count([('employee_id', '=', self.id)])

    commission_count = fields.Integer(string="Commission / Target / Bonus Count", compute='_compute_employee_commission')
