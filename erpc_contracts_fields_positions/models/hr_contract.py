from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    lives_in_yokohama = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Lives in Yokohama', required=True)
    hourly_cost = fields.Monetary('Hourly Cost', compute='_compute_hourly_cost')

    @api.depends('employee_id.hourly_cost')
    def _compute_hourly_cost(self):
        for rec in self:
            rec.hourly_cost = rec.employee_id.hourly_cost
