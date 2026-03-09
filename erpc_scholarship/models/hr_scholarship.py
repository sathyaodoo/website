from odoo import models, fields, api, _


class HrScholarship(models.Model):
    _name = 'hr.scholarship'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Scholarship"

    name = fields.Char(string="Scholarship Name", default="/", readonly=True, help="Name of the Scholarship")
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
    scholarship_amount = fields.Float(string="Scholarship Amount", required=True, help="Scholarship amount")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")
    batch_id = fields.Many2one('hr.payslip.run', string="Payslip Batch", help="Batch Reference")
    paid = fields.Boolean(string="Paid", readonly=True, copy=False)
    note = fields.Text(string="Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.scholarship.seq') or '/'
        return super().create(vals_list)