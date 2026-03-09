from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class PALAccountReport(models.Model):
    _inherit = 'account.report'

    enable_total_column = fields.Boolean(string="Enable Total Column")

    # def _init_options_columns(self, options, previous_options=None):
    #     res = super()._init_options_columns(options, previous_options=previous_options)
    #     _logger.info(f'\n\n\n\n*** _init_options_columns****previous_options****{previous_options}\n\n\n\n.')
    #     _logger.info(f'\n\n\n\n*** _init_options_columns****options****{options}\n\n\n\n.')
    #     if self.enable_total_column and options.get('analytic_accounts_groupby'):
    #         options["columns"].append(
    #             {
    #                 'name': _('Total Analytic'),
    #                 'column_group_key': "total",
    #                 'expression_label': 'balance',
    #                 'sortable': False,
    #                 'figure_type': 'monetary',
    #                 'blank_if_zero': False,
    #                 'style': 'text-align: center; white-space: nowrap;'
    #              }
    #         )
    #         options['column_groups']["total"] = {'forced_domain': [], 'forced_options': {}}
    #     return res

    def _init_options_columns(self, options, previous_options=None):
        res = super()._init_options_columns(options, previous_options=previous_options)
        if self.enable_total_column and options.get('analytic_accounts_groupby'):
            total_column = {
                'name': _('Total Analytic'),
                'column_group_key': "total",
                'expression_label': 'balance',
                'sortable': False,
                'figure_type': 'monetary',
                'blank_if_zero': False,
                'style': 'text-align: center; white-space: nowrap;',
            }

            # Find index of the first column where expression_label == 'planned_budget'
            insert_index = next(
                (i for i, col in enumerate(options['columns']) if col.get('expression_label') == 'planned_budget'),
                len(options['columns'])  # default to append if not found
            )

            # Insert the Total Analytic column before the planned_budget column
            options["columns"].insert(insert_index, total_column)
            options['column_groups']["total"] = {'forced_domain': [], 'forced_options': {}}

        return res

    @api.model
    def _get_profit_and_loss_report_id(self):
        profit_loss_id = self.env["account.report"].search([("name", "=", "Profit and Loss by Financial Group")],
                                                           limit=1)
        return profit_loss_id and profit_loss_id.id or False

    def _add_totals_below_sections(self, lines, options):
        lines = super()._add_totals_below_sections(lines, options)
        lines = self.validate_and_modify_total_lines_via_group_expand(lines, options)
        return lines

    def validate_and_modify_total_lines_via_group_expand(self, lines, options):
        if self.enable_total_column:
            profit_and_loss_av = options.get("available_variants", [])
            is_profit_and_loss = False
            profit_and_loss_id = self._get_profit_and_loss_report_id()
            if profit_and_loss_av:
                is_profit_and_loss = profit_and_loss_av[0].get("id") == profit_and_loss_id
            for line in lines:
                if not line.get("columns", []):
                    continue
                amount_currency = 0
                index, is_total = 0, False
                dict_total_column = False
                for col in line["columns"]:
                    column_group_key = col.get("column_group_key")
                    expression_label = col.get("expression_label")
                    _logger.info(f'\n\n\n\n***otal profit****column_group_key****{column_group_key}\n\n\n\n.')
                    _logger.info(f'\n\n\n\n***otal profit****expression_label****{expression_label}\n\n\n\n.')
                    # add only support Profit and Loss
                    if is_profit_and_loss:
                        if ("'analytic_accounts_list'," in column_group_key
                                and "('analytic_groupby_option', True)" in column_group_key):
                            try:
                                column_group_key = eval(column_group_key)
                                if column_group_key:
                                    analytic_accounts_list = column_group_key[0]
                                    if len(analytic_accounts_list) >= 2:
                                        analytic_accounts_list = analytic_accounts_list[1]
                                        for aal in analytic_accounts_list:
                                            if 'analytic_accounts_list' == aal[0] and len(aal[1]) == 1:
                                                if column_group_key != 'total' and expression_label != 'planned_budget':
                                                    amount_currency += col["no_format"]
                            except Exception as e:
                                amount_currency += 0
                    else:
                        if column_group_key != 'total' and expression_label != 'planned_budget':
                            amount_currency += col["no_format"]
                    if column_group_key == "total" and expression_label != 'planned_budget':
                        index = line["columns"].index(col)
                        dict_total_column = col
                        is_total = True
                if is_total:
                    line["columns"].pop(index)
                    dict_total_column.update({
                        "name": self.format_value(
                            options, amount_currency,
                            currency=dict_total_column.get('currency'),
                            blank_if_zero=dict_total_column.get('blank_if_zero'),
                            figure_type=dict_total_column.get('figure_type'),
                            digits=dict_total_column.get('digits')),
                        "no_format": amount_currency
                    })
                    line["columns"].insert(index, dict_total_column)  # Use insert, not append
                # if is_total:
                #     line["columns"].pop(index)
                #     dict_total_column.update({
                #         "name": self.format_value(
                #             options, amount_currency,
                #             currency=dict_total_column.get('currency'),
                #             blank_if_zero=dict_total_column.get('blank_if_zero'),
                #             figure_type=dict_total_column.get('figure_type'),
                #             digits=dict_total_column.get('digits')),
                #         "no_format": amount_currency
                #     })
                #     line["columns"].append(dict_total_column)
        return lines

    # def _get_lines(self, options, all_column_groups_expression_totals=None, warnings=None):
    #     lines = super()._get_lines(options, all_column_groups_expression_totals=all_column_groups_expression_totals, warnings=warnings)
    #     # modify lines total
    #     lines = self.validate_and_modify_total_lines_via_group_expand(lines, options)
    #     return lines

    def _get_lines(self, options, all_column_groups_expression_totals=None, warnings=None):
        lines = super()._get_lines(options, all_column_groups_expression_totals=all_column_groups_expression_totals,
                                   warnings=warnings)
        # modify lines total
        lines = self.validate_and_modify_total_lines_via_group_expand(lines, options)
        if self.enable_total_column and options.get('analytic_accounts_groupby'):
            profit_and_loss_av = options.get("available_variants", [])
            is_profit_and_loss = False
            profit_and_loss_id = self._get_profit_and_loss_report_id()
            if profit_and_loss_av:
                is_profit_and_loss = profit_and_loss_av[0].get("id") == profit_and_loss_id

            net_profit_total = 0.0
            total_income_total = 0.0
            gross_profit_total = 0.0
            landed_cost_6018_total = 0.0
            landed_cost_fp_total = 0.0
            expenses_net_total = 0.0
            cost_of_revenue_total = 0.0
            if is_profit_and_loss:
                analytic_ids = self.env['account.analytic.account'].browse(options.get('analytic_accounts_groupby'))
                _logger.info(f'\n\n\n\n***_get_lines****analytic_ids****{analytic_ids}\n\n\n\n.')
                if analytic_ids:
                    Analytic = self.env['account.analytic.account']
                    for line in lines:
                        # target just your two special codes:
                        # if line.get('code') in ('NPP', 'GMP', 'LCP', 'LC60', 'LCFPU', 'NLC'):
                        if line.get('name') in (
                        'Net Profit (%)', 'Gross Margin Profit (%)', 'Landed Cost (%)', 'Net Landed Cost'):
                            for col in line.get('columns', []):
                                column_group_key = col.get("column_group_key")
                                try:
                                    column_group_key = eval(column_group_key)
                                    if column_group_key:
                                        analytic_accounts_list = column_group_key[0]
                                        _logger.info(
                                            f'\n\n\n\n***_get_lines****analytic_accounts_list*4444***{analytic_accounts_list}\n\n\n\n.')
                                        if len(analytic_accounts_list) >= 2:
                                            analytic_accounts_list = analytic_accounts_list[1]
                                            _logger.info(
                                                f'\n\n\n\n***_get_lines****analytic_accounts_list*5555***{analytic_accounts_list}\n\n\n\n.')
                                            for aal in analytic_accounts_list:
                                                if 'analytic_accounts_list' == aal[0] and len(aal[1]) == 1:
                                                    aal_id = aal[1][0]
                                                    account = Analytic.browse(int(aal_id))
                                                    _logger.info(
                                                        f'\n\n\n\n***_get_lines****aal*5555*aal_id**{aal, aal_id}\n\n\n\n.')
                                                    if not account:
                                                        continue
                                                    account_company_id = account.company_id.id
                                                    _logger.info(
                                                        f'\n\n\n\n***_get_lines****account_company_id**{account_company_id}\n\n\n\n.')
                                                    # if account_company_id != 1:
                                                    col['no_format'] = 0.0  # zero out
                                                    col['name'] = ''  # blank display
                                                    col['is_zero'] = True  # mark as zero

                                except Exception:
                                    _logger.warning(f"Could not eval column_group_key {column_group_key}")
                # Find lines using their names
                for line in lines:
                    if line.get('name') == 'Net Profit':  # Add this condition forNet Profit
                        for col in line.get('columns', []):
                            if col.get('column_group_key') == 'total':
                                net_profit_total = col.get('no_format', 0.0)
                                break
                    elif line.get('name') == 'Income':  # Add this condition for Income
                        for col in line.get('columns', []):
                            if col.get('column_group_key') == 'total':
                                total_income_total = col.get('no_format', 0.0)
                                break
                    elif line.get('name') == 'Gross Profit':  # Add this condition for Gross Profit
                        for col in line.get('columns', []):
                            if col.get('column_group_key') == 'total':
                                gross_profit_total = col.get('no_format', 0.0)
                                break
                    elif line.get('name') == '6018 LC':  # Add this condition for 6018 LC
                        for col in line.get('columns', []):
                            if col.get('column_group_key') == 'total':
                                landed_cost_6018_total = col.get('no_format', 0.0)
                                break
                    elif line.get('name') == 'Foreign Purchase':  # Add this condition for Foreign Purchase
                        for col in line.get('columns', []):
                            if col.get('column_group_key') == 'total':
                                landed_cost_fp_total = col.get('no_format', 0.0)
                                break
                    elif line.get('name') == 'Expenses NET':  # Add this condition for Expenses NET
                        for col in line.get('columns', []):
                            if col.get('column_group_key') == 'total':
                                expenses_net_total = col.get('no_format', 0.0)
                                break
                    elif line.get('name') == 'Cost of Revenue':  # Add this condition for Cost of Revenue
                        for col in line.get('columns', []):
                            if col.get('column_group_key') == 'total':
                                cost_of_revenue_total = col.get('no_format', 0.0)
                                break

                # Now, iterate through the lines again to find 'Net Profit (%)' and update its 'total' column
                for line in lines:
                    if line.get('name') == 'Net Profit (%)':
                        for col in line.get('columns', []):
                            if col.get('column_group_key') == 'total':
                                if total_income_total != 0:
                                    calculated_net_profit_percentage = (net_profit_total / total_income_total) * 100.0
                                else:
                                    calculated_net_profit_percentage = 0.0

                                col['no_format'] = calculated_net_profit_percentage
                                col['name'] = f'{calculated_net_profit_percentage :.2f}%'
                                break
                        break  # Exit after finding and updating the line

                # Now, iterate through the lines again to find 'Gross Margin Profit (%)' and update its 'total' column
                for line in lines:
                    if line.get('name') == 'Gross Margin Profit (%)':
                        for col in line.get('columns', []):
                            if col.get('column_group_key') == 'total':
                                if total_income_total != 0:
                                    calculated_gross_margin_percentage = (
                                                                                     gross_profit_total / total_income_total) * 100.0
                                else:
                                    calculated_gross_margin_percentage = 0.0

                                col['no_format'] = calculated_gross_margin_percentage
                                col['name'] = f'{calculated_gross_margin_percentage:.2f}%'
                                break
                        break  # Exit after finding and updating the Gross Margin Profit (%) line

                # Now, iterate through the lines again to find 'Landed Cost (%)' and update its 'total' column
                for line in lines:
                    if line.get('name') == 'Landed Cost (%)':
                        for col in line.get('columns', []):
                            if col.get('column_group_key') == 'total':
                                if landed_cost_fp_total != 0:
                                    calculated_landed_cost_percentage = (
                                                                                    landed_cost_6018_total / landed_cost_fp_total) * 100.0
                                else:
                                    calculated_landed_cost_percentage = 0.0

                                col['no_format'] = calculated_landed_cost_percentage
                                col['name'] = f'{calculated_landed_cost_percentage:.2f}%'
                                break
                        break  # Exit after finding and updating the Landed Cost (%) line

                # Now, iterate through the lines again to find 'Landed Cost (%)' and update its 'total' column
                for line in lines:
                    if line.get('name') == 'Net Landed Cost':
                        for col in line.get('columns', []):
                            if col.get('column_group_key') == 'total':
                                if cost_of_revenue_total != 0:
                                    calculated_net_landed_cost_factor = (expenses_net_total/cost_of_revenue_total) + 1
                                else:
                                    calculated_net_landed_cost_factor = 0.0

                                col['no_format'] = calculated_net_landed_cost_factor
                                col['name'] = f'{calculated_net_landed_cost_factor:.2f}'
                                break
                        break  # Exit after finding and updating the Landed Cost (%) line

        return lines
