from odoo import api, models, fields


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    erpc_currency = fields.Many2one('res.currency', string='Currency')
