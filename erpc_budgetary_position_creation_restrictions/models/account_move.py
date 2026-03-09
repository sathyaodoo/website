from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # TODO : to uncomment
    # def _validate_budget(self):
    #     for move in self:
    #         for line in move.line_ids:
    #             if line.financial_group_id and line.account_id:
    #                 budget_positions = self.env['account.budget.post'].sudo().search([
    #                     ('financial_group_id', '=', line.financial_group_id.id),
    #                     ('account_ids.code', '=', line.account_id.code)
    #                 ])
    #                 _logger.info(f'\n\n\n\n*****budget_positions****{budget_positions}\n\n\n\n.')
    #                 date = move.invoice_date if move.invoice_date else move.date
    #                 _logger.info(f'\n\n\n\n*****date****{date}\n\n\n\n.')
    #                 budget_lines = self.env['crossovered.budget.lines'].sudo().search([
    #                     ('general_budget_id', 'in', budget_positions.ids),
    #                     ('crossovered_budget_id.state', 'in', ('validate', 'done')),
    #                     ('date_from', '<=', date),
    #                     ('date_to', '>=', date)
    #                 ])
    #                 _logger.info(f'\n\n\n\n*****budget_lines****{budget_lines}\n\n\n\n.')
    #                 total_planned_amount = sum(budget_lines.mapped('planned_amount'))
    #                 total_practical_amount = sum(budget_lines.mapped('practical_amount'))
    #                 _logger.info(f'\n\n\n\n*****total_planned_amount****{total_planned_amount}\n\n\n\n.')
    #                 _logger.info(f'\n\n\n\n*****total_practical_amount****{total_practical_amount}\n\n\n\n.')

    #                 amount_by_month = 0
    #                 if line.deferred_start_date and line.deferred_end_date:
    #                     _logger.info(f"Start Date: {line.deferred_start_date}, End Date: {line.deferred_end_date}")
    #                     adjusted_end_date = line.deferred_end_date + timedelta(days=1)
    #                     duration1 = relativedelta(line.deferred_end_date, line.deferred_start_date)
    #                     duration = relativedelta(adjusted_end_date, line.deferred_start_date)
    #                     _logger.info(f'\n\n\n\n*****duration****{duration, duration1}\n\n\n\n.')
    #                     months = duration.years * 12 + duration.months
    #                     _logger.info(f'\n\n\n\n*****months****{months}\n\n\n\n.')
    #                     amount_by_month = abs(line.balance) / months if months != 0 else 0
    #                     _logger.info(f'\n\n\n\n*****amount_by_month****{amount_by_month}\n\n\n\n.')

    #                 balance_line = abs(line.balance) if amount_by_month == 0 else amount_by_month
    #                 _logger.info(f'\n\n\n\n*****balance_line****{balance_line}\n\n\n\n.')
    #                 amount_to_have = abs(total_practical_amount) + balance_line
    #                 _logger.info(f'\n\n\n\n*****amount_to_have****{amount_to_have}\n\n\n\n.')
    #                 move_type = dict(self._fields['move_type'].selection).get(self.move_type)
    #                 if budget_lines:
    #                     start_date = budget_lines.mapped('date_from')[0]
    #                     end_date = budget_lines.mapped('date_to')[0]
    #                     _logger.info(f'\n\n\n\n*****date_from date_to****{start_date, end_date}\n\n\n\n.')
    #                     draft_deferral_lines = self.env['account.move.line'].sudo().search(
    #                         [("move_id.deferred_original_move_ids", "!=", False), ("parent_state", "=", "draft"),
    #                          ("date", ">=", start_date), ("date", "<=", end_date),
    #                          ("financial_group_id", "=", line.financial_group_id.id),
    #                          ("id", "!=", line.id)])
    #                     _logger.info(f'\n\n\n\n*****draft_deferral_lines****{draft_deferral_lines}\n\n\n\n.')
    #                     if draft_deferral_lines:
    #                         draft_deferral_amount = sum(draft_deferral_lines.mapped('balance'))
    #                         _logger.info(f'\n\n\n\n*****draft_deferral_amount****{draft_deferral_amount}\n\n\n\n.')

    #                     if line.analytic_distribution:
    #                         items = line.analytic_distribution.items()
    #                         _logger.info(f'\n\n\n\n*****items****{items}\n\n\n\n.')
    #                         for account_id, percentage in line.analytic_distribution.items():
    #                             _logger.debug("Processing analytic account ID: %s", account_id)
    #                             analytic_account = self.env['account.analytic.account'].sudo().search(
    #                                 [('id', '=', account_id)], limit=1)

    #                             analytic_budget_lines = self.env['crossovered.budget.lines'].sudo().search([
    #                                 ('general_budget_id', 'in', budget_positions.ids),
    #                                 ('crossovered_budget_id.state', 'in', ('validate', 'done')),
    #                                 ('date_from', '<=', date),
    #                                 ('date_to', '>=', date),
    #                                 ('analytic_account_id.name', '=', analytic_account.name)
    #                             ])
    #                             if draft_deferral_lines:
    #                                 if analytic_budget_lines:
    #                                     _logger.info(
    #                                         f'\n\n\n\n*****draft_deferral_lines**all**{draft_deferral_lines}\n\n\n\n.')
    #                                     for draft_line in draft_deferral_lines:
    #                                         # Check if the draft line has the account_id in its analytic_distribution
    #                                         _logger.info(
    #                                             f'\n\n\n\n*****str(account_id)****{str(account_id)}\n\n\n\n.')
    #                                         _logger.info(
    #                                             f'\n\n\n\n*****draft_line.analytic_distribution****{draft_line.analytic_distribution}\n\n\n\n.')
    #                                         if str(account_id) in draft_line.analytic_distribution:
    #                                             # Get the percentage for this account from the draft line's distribution
    #                                             draft_percentage = draft_line.analytic_distribution[str(account_id)]

    #                                             # Calculate the amount for this account based on the percentage
    #                                             draft_amount = (draft_percentage / 100) * abs(draft_line.balance)

    #                                             # Add this draft amount to the analytic_amount_to_have
    #                                             # analytic_total_practical_amount = sum(analytic_budget_lines.mapped('practical_amount')) + draft_amount
    #                                             _logger.info(
    #                                                 f"Added draft line amount to analytic_total_practical_amount for account {account_id}: {draft_amount}."
    #                                             )
    #                                         else:
    #                                             draft_amount = 0
    #                                             _logger.info(
    #                                                 f'\n\n\n\n******draft_amount*1111**{draft_amount}\n\n\n\n.')

    #                                 else:
    #                                     draft_amount = abs(draft_deferral_amount)
    #                                     _logger.info(
    #                                         f'\n\n\n\n******draft_amount*222**{draft_amount}\n\n\n\n.')
    #                             else:
    #                                 draft_amount = 0
    #                                 _logger.info(
    #                                     f'\n\n\n\n******draft_amount*333**{draft_amount}\n\n\n\n.')
    #                             analytic_total_planned_amount = sum(analytic_budget_lines.mapped(
    #                                 'planned_amount')) if analytic_budget_lines else total_planned_amount
    #                             analytic_total_practical_amount = sum(analytic_budget_lines.mapped(
    #                                 'practical_amount')) + draft_amount if analytic_budget_lines else total_practical_amount + draft_amount
    #                             analytic_amount_to_have = abs(analytic_total_practical_amount) + (
    #                                     (percentage / 100) * abs(line.balance)) if analytic_budget_lines else (
    #                                     amount_to_have + draft_amount)
    #                             ### to add case of draft items with analytic account : amount_to have = analytic_amount_to_have + amount of the draft entries
    #                             _logger.info(
    #                                 f'\n\n\n\n*****analytic_total_planned_amount****{analytic_total_planned_amount}\n\n\n\n.')
    #                             _logger.info(
    #                                 f'\n\n\n\n*****analytic_total_practical_amount****{analytic_total_practical_amount}\n\n\n\n.')
    #                             _logger.info(
    #                                 f'\n\n\n\n*****analytic_amount_to_have****{analytic_amount_to_have}\n\n\n\n.')

    #                             if analytic_amount_to_have > abs(analytic_total_planned_amount):
    #                                 _logger.info(f'\n\n\n\n*****in condition111****{amount_to_have}\n\n\n\n.')
    #                                 if analytic_budget_lines:
    #                                     raise ValidationError(
    #                                         f"You can not confirm this {move_type} "
    #                                         f"because the amount exceeds the allocated budget for analytic {analytic_account.name}"
    #                                         f" Please Contact the Administrator to give you budget or Confirm it for you"
    #                                     )
    #                                 else:
    #                                     if abs(total_practical_amount) + draft_amount + balance_line > abs(
    #                                             total_planned_amount):
    #                                         _logger.info(f'\n\n\n\n*****in condition2222****{amount_to_have}\n\n\n\n.')
    #                                         if draft_amount != 0:
    #                                             raise ValidationError(
    #                                                 f"You can not confirm this {move_type} "
    #                                                 f"because the amount exceeds the allocated budget"
    #                                                 f" and there are deferrals entries not posted yet. "
    #                                                 f"Please Contact the Administrator to give you budget or Confirm it for you"
    #                                             )
    #                                         else:
    #                                             raise ValidationError(
    #                                                 f"You can not confirm this {move_type} "
    #                                                 f"because the amount exceeds the allocated budget. "
    #                                                 f"Please Contact the Administrator to give you budget or Confirm it for you"
    #                                             )
    #                     else:

    #                         if abs(total_practical_amount) + abs(draft_deferral_amount) + balance_line > abs(
    #                                 total_planned_amount):
    #                             _logger.info(f'\n\n\n\n*****in condition****{amount_to_have}\n\n\n\n.')
    #                             if draft_deferral_amount != 0:
    #                                 raise ValidationError(
    #                                     f"You can not confirm this {move_type} "
    #                                     f"because the amount exceeds the allocated budget"
    #                                     f" and there are deferrals entries not posted yet. "
    #                                     f"Please Contact the Administrator to give you budget or Confirm it for you"
    #                                 )
    #                             else:
    #                                 raise ValidationError(
    #                                     f"You can not confirm this {move_type} "
    #                                     f"because the amount exceeds the allocated budget. "
    #                                     f"Please Contact the Administrator to give you budget or Confirm it for you"
    #                                 )
    #                 else:
    #                     if line.account_type in ('expense', 'expense_depreciation', 'income_other'):
    #                         raise ValidationError(
    #                             f"You can not confirm this {move_type} "
    #                             f"because there is no allocated budget. "
    #                             f"Please Contact the Administrator to give you budget or Confirm it for you"
    #                         )
    #                     else:
    #                         _logger.info(f'\n\n\n\n*****move_type****{move_type}\n\n\n\n.')

    # def action_post(self):
    #     if self.company_id.id == 1:
    #         _logger.info(f'\n\n\n\n*****marwan****{self.company_id.name}\n\n\n\n.')
    #         if not self.env.user.has_group('erpc_budgetary_position_creation_restrictions.group_budget_admin'):
    #             self._validate_budget()
    #     return super(AccountMove, self).action_post()
