# from odoo import api, fields, models, _
# from odoo.exceptions import ValidationError
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class CrossoveredBudget(models.Model):
#     _inherit = "crossovered.budget"
#
#     total_budget_amount = fields.Float(
#         string="Total Planned Amount", compute="_compute_total_budget", store=True
#     )
#
#     @api.depends(
#         "crossovered_budget_line",
#         "crossovered_budget_line.planned_amount",
#     )
#     @api.depends_context("company_id")
#     def _compute_total_budget(self):
#         for budget in self:
#             total_planned = 0.0
#
#             for line in budget.crossovered_budget_line:
#                 total_planned += line.planned_amount
#
#             budget.total_budget_amount = (
#                 total_planned
#             )
#
#     def unlink(self):
#         for record in self:
#             if record.state in ["validate", "done"]:
#                 raise ValidationError(
#                     _("You can't delete a validated or a done budget.")
#                 )
#         return super(CrossoveredBudget, self).unlink()
