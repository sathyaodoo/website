from odoo import models, fields, api


class HrVersion(models.Model):
    _inherit = 'hr.version'

    name = fields.Char(default="/")
    # analytic_account_id = fields.Many2one(
    #     'account.analytic.account', 'Analytic Account', check_company=True, readonly=True)

    analytic_account_unique_entry = fields.Many2one(
        'account.analytic.account', 'Analytic Account Unique Entry', check_company=True, help='This field is used in the payroll entry and must be filled by concerned department of the employee')

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = self.env["ir.sequence"].next_by_code("erpc_seq_contract")
        records = super(HrVersion, self).create(vals_list)
        return records

