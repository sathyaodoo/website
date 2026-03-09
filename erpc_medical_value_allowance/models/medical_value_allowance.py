from odoo import models, fields, api, _


class MedicalValueAllowance(models.Model):
    _name = 'medical.value.allowance'

    employee_id = fields.Many2one('hr.employee', string='Employee', help="Employee name")
    date = fields.Date(string="Date", default=fields.Date.today(), help="Date")
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id', store=True)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", string="Job Position", help="Job position")
    medical_value_allowance = fields.Float(string="Medical Value Allowance Amount", required=True)
    # company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env['res.company'].search([('name', '=', 'M HR')], limit=1).id, string='Company')
    company_id = fields.Many2one('res.company', default=11, string='Company')
    currency_id = fields.Many2one('res.currency', string='Currency', help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)

    paid = fields.Boolean(string="Paid", readonly=True, copy=False)
    description = fields.Text(string="Description")
