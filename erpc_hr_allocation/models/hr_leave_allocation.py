from odoo import fields, models, api


class HRLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    erpc_taken_leaves = fields.Float(compute='_compute_taken_leaves', string='Taken Leaves', store=True,
                                     precompute=True, copy=False)

    #to fix
    # @api.depends('employee_id', 'holiday_status_id', 'leaves_taken')
    def _compute_taken_leaves(self):
        for allocation in self:
            allocation.erpc_taken_leaves = allocation.leaves_taken
