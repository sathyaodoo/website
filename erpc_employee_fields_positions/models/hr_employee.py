from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    department_id = fields.Many2one(related="version_id.department_id", tracking=True, store=True)
    job_id = fields.Many2one(related="version_id.job_id", tracking=True, store=True)
    registration_number = fields.Char('Fiscal No.', groups="hr.group_hr_user", copy=False)
    is_representation_fees = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="Representation Fees", help="This field is checked for the CEO", default='no', required=True)
    contract_end_date = fields.Date(related="version_id.date_end", string='Contract End Date')
    wage = fields.Monetary(string='Wage', related="version_id.wage")
    erpc_state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
    ], string='Status', copy=False,
        tracking=True, default='draft')
    contact_id = fields.Integer(related="address_id.id", string="Contact ID")
    nssf_entry_date = fields.Date(string='NSSF Entry Date')
    nssf_leave_date = fields.Date(string='NSSF Leave Date')
    r3_delivery_date = fields.Date(string='R3 Delivery Date')
    nssf_wage_usd = fields.Float('NSSF Wage USD', related="version_id.nssf_wage")
    nssf_wage_lbp = fields.Float(related="version_id.nssf_wage_lbp", string='NSSF Wage LBP')
    family_info_ids = fields.One2many('family.info', 'erpc_employee_id', string='Family Info')

    def action_confirm(self):
        self.write({'erpc_state': "confirm"})
