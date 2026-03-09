from odoo import models, _, fields, api
from odoo.tools import float_compare
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, formatLang, format_date, xlsxwriter
from collections import defaultdict
from ast import literal_eval
from datetime import timedelta
import logging

from odoo.osv.expression import expression
from odoo.tools.sql import SQL

_logger = logging.getLogger(__name__)


# class AccountMoveLine(models.Model):
#     _inherit = 'account.move.line'
#
#     planned_budget = fields.Monetary(
#         string='Panned Budget',
#         compute='_compute_planned_budget', store=True, precompute=True,
#         currency_field='company_currency_id',
#     )
#
#     @api.depends('account_id', 'financial_group_id', 'move_id.date', 'account_id.general_budget_id.account_ids')
#     def _compute_planned_budget(self):
#         for line in self:
#             if line.financial_group_id:
#                 budget_positions = self.env['account.budget.post'].search([
#                     ('financial_group_id', '=', line.financial_group_id.id),
#                     ('account_ids.code', '=', line.account_id.code)
#                 ])
#                 date = line.move_id.invoice_date if line.move_id.invoice_date else line.move_id.date
#                 _logger.info(
#                     f'\n\n\n\n***budget_positions****_compute_planned_budget****{budget_positions, line.financial_group_id, date}\n\n\n\n.')
#                 budget_lines = self.env['crossovered.budget.lines'].search([
#                     ('general_budget_id', 'in', budget_positions.ids),
#                     ('date_from', '<=', date),
#                     ('date_to', '>=', date)
#                 ])
#                 total_planned_amount = sum(budget_lines.mapped('planned_amount'))
#                 line.planned_budget = total_planned_amount
#             else:
#                 line.planned_budget = 0


class AccountReport(models.Model):
    _inherit = 'account.report'

    def _build_columns_from_column_group_vals(self, options, all_column_group_vals_in_order):
        def _generate_domain_from_horizontal_group_hash_key_tuple(group_hash_key):
            domain = []
            for field_name, field_value in group_hash_key:
                domain.append((field_name, '=', field_value))
            return domain

        columns = []
        column_groups = {}
        for column_group_val in all_column_group_vals_in_order:
            horizontal_group_key_tuple = self._get_dict_hashable_key_tuple(
                column_group_val['horizontal_groupby_element'])
            column_group_key = str(self._get_dict_hashable_key_tuple(column_group_val))

            column_groups[column_group_key] = {
                'forced_options': column_group_val['forced_options'],
                'forced_domain': _generate_domain_from_horizontal_group_hash_key_tuple(horizontal_group_key_tuple),
            }

            for report_column in self.column_ids:
                if (
                        report_column.expression_label == 'planned_budget'
                        and column_group_val['forced_options'].get('analytic_groupby_option') is True
                ):
                    continue

                columns.append({
                    'name': report_column.name,
                    'column_group_key': column_group_key,
                    'expression_label': report_column.expression_label,
                    'sortable': report_column.sortable,
                    'figure_type': report_column.figure_type,
                    'blank_if_zero': report_column.blank_if_zero,
                    'style': "text-align: center; white-space: nowrap;",
                })

        return columns, column_groups

    def _compute_formula_batch_with_engine_domain(self, options, date_scope, formulas_dict, current_groupby,
                                                  next_groupby, offset=0, limit=None, warnings=None):
        current_report_id = options['report_id']
        profit_and_loss_report_id = self.env.ref('erpc_profit_and_loss_by_finance.profit_and_loss_by_finance').id

        if current_report_id == profit_and_loss_report_id:
            def _format_result_depending_on_groupby(formula_rslt):
                if not current_groupby:
                    if formula_rslt:
                        return formula_rslt[0][1]
                    else:
                        return {
                            'sum': 0,
                            'budget_sum': 0,
                            'sum_if_pos': 0,
                            'sum_if_neg': 0,
                            'count_rows': 0,
                            'has_sublines': False,
                        }
                return formula_rslt

            self._check_groupby_fields(
                (next_groupby.split(',') if next_groupby else []) + ([current_groupby] if current_groupby else []))

            groupby_sql = f'account_move_line.{current_groupby}' if current_groupby else None
            ct_query = self._get_query_currency_table(options)

            rslt = {}
            date_from = options['date']['date_from']
            date_to = options['date']['date_to']

            for formula, expressions in formulas_dict.items():
                try:
                    line_domain = literal_eval(formula)
                except (ValueError, SyntaxError):
                    raise UserError(_("Invalid domain formula in expression %r of line %r: %s", expressions.label,
                                      expressions.report_line_id.name, formula))

                tables, where_clause, where_params = self._query_get(options, date_scope, domain=line_domain)
                tail_query, tail_params = self._get_engine_query_tail(offset, limit)

                query = f"""
                    SELECT
                        COALESCE(SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)), 0.0) AS sum,
                        0.0 AS budget_sum,  -- Placeholder, will be filled later
                        COUNT(DISTINCT account_move_line.{next_groupby.split(',')[0] if next_groupby else 'id'}) AS count_rows
                        {f', {groupby_sql} AS grouping_key' if groupby_sql else ''}
                    FROM {tables}
                    JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
                    WHERE {where_clause}
                    {f' GROUP BY {groupby_sql}' if groupby_sql else ''}
                    {f' ORDER BY {groupby_sql}' if groupby_sql else ''}
                    {tail_query}
                """

                self._cr.execute(query, where_params + tail_params)
                all_query_res = self._cr.dictfetchall()

                formula_rslt = []
                total_sum = 0

                grouping_keys = [r['grouping_key'] for r in all_query_res if 'grouping_key' in r]

                # Budget lookup if grouped by financial_group_id
                budget_amount_map = {}
                if current_groupby == 'financial_group_id' and grouping_keys:
                    self._cr.execute("""
                        SELECT
                            gb.financial_group_id,
                            SUM(b.planned_amount) AS total_planned
                        FROM crossovered_budget_lines b
                        JOIN account_budget_post gb ON gb.id = b.general_budget_id
                        WHERE b.date_from <= %s
                          AND b.date_from >= %s
                          AND gb.financial_group_id = ANY(%s)
                        GROUP BY gb.financial_group_id
                    """, [date_to, date_from, grouping_keys])
                    budget_lines = self._cr.dictfetchall()
                    budget_amount_map = {line['financial_group_id']: line['total_planned'] for line in budget_lines}

                for query_res in all_query_res:
                    grouping_key = query_res.get('grouping_key')
                    res_sum = query_res['sum']
                    nb_lines = query_res['count_rows']
                    total_sum += res_sum

                    # Use planned_amount if not grouped by account_id
                    planned_amount = budget_amount_map.get(grouping_key, 0.0)
                    # budget_sum = 0 if current_groupby == 'account_id' else planned_amount
                    if current_groupby == 'financial_group_id':
                        budget_sum = planned_amount
                    elif current_groupby == 'account_id':
                        budget_sum = 0
                    else:
                        expense_accounts = self.env['account.account'].search([
                            ('account_type', '=', 'expense'),
                        ])

                        # Get budgetary positions that are linked to these expense accounts
                        expense_budget_posts = self.env['account.budget.post'].search([
                            ('account_ids', 'in', expense_accounts.ids)
                        ])
                        # Extract the unique financial_group_ids from these budgetary positions
                        financial_group_ids_for_expenses = expense_budget_posts.mapped('financial_group_id').ids

                        _logger.info(f"Financial Group IDs for Expenses: {financial_group_ids_for_expenses}")

                        depreciation_accounts = self.env['account.account'].search([
                            ('account_type', '=', 'expense_depreciation')
                        ])
                        # Get budgetary positions that are linked to these expense_depreciation accounts
                        depreciation_budget_posts = self.env['account.budget.post'].search([
                            ('account_ids', 'in', depreciation_accounts.ids)
                        ])
                        # Extract the unique financial_group_ids from these budgetary positions
                        financial_group_ids_for_depreciation = depreciation_budget_posts.mapped(
                            'financial_group_id').ids

                        _logger.info(f"Financial Group IDs for Depreciation: {financial_group_ids_for_depreciation}")

                        total_planned_budget_for_expenses = 0.0
                        total_planned_budget_for_depreciation = 0.0

                        if financial_group_ids_for_expenses:

                            self.env.cr.execute("""
                                            SELECT SUM(cbl.planned_amount)
                                            FROM crossovered_budget_lines cbl
                                            JOIN account_budget_post abp ON cbl.general_budget_id = abp.id
                                            WHERE abp.financial_group_id = ANY(%s)
                                              AND cbl.date_from <= %s
                                              AND cbl.date_to >= %s
                                        """, [financial_group_ids_for_expenses, date_to, date_from])

                            query_result = self.env.cr.fetchone()
                            if query_result and query_result[0] is not None:
                                total_planned_budget_for_expenses = query_result[0]

                        _logger.info(f"Total Planned Budget for Expenses: {total_planned_budget_for_expenses}")

                        if financial_group_ids_for_depreciation:

                            self.env.cr.execute("""
                                            SELECT SUM(cbl.planned_amount)
                                            FROM crossovered_budget_lines cbl
                                            JOIN account_budget_post abp ON cbl.general_budget_id = abp.id
                                            WHERE abp.financial_group_id = ANY(%s)
                                              AND cbl.date_from <= %s
                                              AND cbl.date_to >= %s
                                        """, [financial_group_ids_for_depreciation, date_to, date_from])

                            query_result = self.env.cr.fetchone()
                            if query_result and query_result[0] is not None:
                                total_planned_budget_for_depreciation = query_result[0]

                        _logger.info(f"Total Planned Budget for Depreciation: {total_planned_budget_for_depreciation}")

                        is_expenses_planned_budget_expression = False
                        is_depreciation_planned_budget_expression = False
                        for expr in expressions:
                            if expr.report_line_id.code == 'EXP' and expr.label == 'planned_budget' and expr.subformula == 'budget_sum':
                                is_expenses_planned_budget_expression = True
                            elif expr.report_line_id.code == 'DEP' and expr.label == 'planned_budget' and expr.subformula == 'budget_sum':
                                is_depreciation_planned_budget_expression = True
                        if is_expenses_planned_budget_expression:
                            budget_sum = total_planned_budget_for_expenses
                        elif is_depreciation_planned_budget_expression:
                            budget_sum = total_planned_budget_for_depreciation
                        else:
                            budget_sum = 0

                    totals = {
                        'sum': res_sum,
                        'budget_sum': budget_sum,
                        'sum_if_pos': 0,
                        'sum_if_neg': 0,
                        'count_rows': nb_lines,
                        'has_sublines': nb_lines > 0,
                    }
                    formula_rslt.append((grouping_key, totals))

                expressions_by_sign_policy = defaultdict(lambda: self.env['account.report.expression'])
                for expression in expressions:
                    subformula_without_sign = expression.subformula.replace('-', '').strip()
                    if subformula_without_sign in ('sum_if_pos', 'sum_if_neg'):
                        expressions_by_sign_policy[subformula_without_sign] += expression
                    else:
                        expressions_by_sign_policy['no_sign_check'] += expression

                if expressions_by_sign_policy['sum_if_pos'] or expressions_by_sign_policy['sum_if_neg']:
                    sign_policy_with_value = 'sum_if_pos' if self.env.company.currency_id.compare_amounts(total_sum,
                                                                                                          0.0) >= 0 else 'sum_if_neg'
                    formula_rslt_with_sign = [(grouping_key, {**totals, sign_policy_with_value: totals['sum']}) for
                                              grouping_key, totals in formula_rslt]

                    for sign_policy in ('sum_if_pos', 'sum_if_neg'):
                        policy_expressions = expressions_by_sign_policy[sign_policy]
                        if policy_expressions:
                            if sign_policy == sign_policy_with_value:
                                rslt[(formula, policy_expressions)] = _format_result_depending_on_groupby(
                                    formula_rslt_with_sign)
                            else:
                                rslt[(formula, policy_expressions)] = _format_result_depending_on_groupby([])

                if expressions_by_sign_policy['no_sign_check']:
                    rslt[(formula, expressions_by_sign_policy['no_sign_check'])] = _format_result_depending_on_groupby(
                        formula_rslt)

            return rslt
        else:
            return super()._compute_formula_batch_with_engine_domain(options, date_scope, formulas_dict,
                                                                     current_groupby,
                                                                     next_groupby, offset, limit, warnings)

    # def _get_lines(self, options, all_column_groups_expression_totals=None, warnings=None):

    #     lines = super()._get_lines(options, all_column_groups_expression_totals=all_column_groups_expression_totals,
    #                                warnings=warnings)

    #     # Get the ID of your custom P&L report
    #     profit_and_loss_report_id = self.env.ref('erpc_profit_and_loss_by_finance.profit_and_loss_by_finance').id

    #     # Check if the current report is your custom P&L
    #     if options['report_id'] == profit_and_loss_report_id:
    #         date_from = options['date']['date_from']
    #         date_to = options['date']['date_to']

    #         expense_accounts = self.env['account.account'].search([
    #             ('account_type', '=', 'expense'),
    #         ])

    #         # Get budgetary positions that are linked to these expense accounts
    #         expense_budget_posts = self.env['account.budget.post'].search([
    #             ('account_ids', 'in', expense_accounts.ids)
    #         ])

    #         # Extract the unique financial_group_ids from these budgetary positions
    #         financial_group_ids_for_expenses = expense_budget_posts.mapped('financial_group_id').ids

    #         _logger.info(f"Financial Group IDs for Expenses: {financial_group_ids_for_expenses}")

    #         total_planned_budget_for_expenses = 0.0

    #         if financial_group_ids_for_expenses:

    #             self.env.cr.execute("""
    #                 SELECT SUM(cbl.planned_amount)
    #                 FROM crossovered_budget_lines cbl
    #                 JOIN account_budget_post abp ON cbl.general_budget_id = abp.id
    #                 WHERE abp.financial_group_id = ANY(%s)
    #                   AND cbl.date_from <= %s
    #                   AND cbl.date_to >= %s
    #             """, [financial_group_ids_for_expenses, date_to, date_from])

    #             query_result = self.env.cr.fetchone()
    #             if query_result and query_result[0] is not None:
    #                 total_planned_budget_for_expenses = query_result[0]

    #         _logger.info(f"Total Planned Budget for Expenses: {total_planned_budget_for_expenses}")

    #         expenses_line_code = 'Expenses'
    #         for line in lines:
    #             if line.get('name') == expenses_line_code:

    #                 # Let's find the 'planned_budget' column by its expression_label
    #                 for col_idx, col_data in enumerate(line.get('columns', [])):
    #                     if col_data.get('expression_label') == 'planned_budget':  # Matches the XML expression_label
    #                         # Update the 'amount' field of this specific column's data.
    #                         line['columns'][col_idx]['amount'] = total_planned_budget_for_expenses
    #                         line['columns'][col_idx]['no_format'] = total_planned_budget_for_expenses
    #                         break  # Found and updated, move to next line

    #                 # If you just want to append it as a new cell at the end (less common for core financial reports):
    #                 # line['columns'].append({
    #                 #     'name': self.env.company.currency_id.format(total_planned_budget_for_expenses),
    #                 #     'amount': total_planned_budget_for_expenses,
    #                 #     'no_format': total_planned_budget_for_expenses,
    #                 #     'class': 'number', # or 'o_account_report_line_budget' if you have specific styling
    #                 #     'expression_label': 'manual_planned_budget', # A custom label if it's not a pre-defined column
    #                 # })
    #                 break  # Found the expenses line, no need to continue iterating lines

    #     return lines


