from odoo import api, models, fields


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    currency_id = fields.Many2one('res.currency', related='salary_rule_id.erpc_currency')

