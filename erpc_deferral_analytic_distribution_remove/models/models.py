from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _get_deferred_lines_values(self, account_id, balance, ref, analytic_distribution, line=None):
        _logger.info(
            f'\n\n\n\n*****_get_deferred_lines_values***analytic_distribution***{account_id, analytic_distribution}\n\n\n\n.')
        values = super(AccountMoveLine, self)._get_deferred_lines_values(
            account_id, balance, ref, analytic_distribution, line
        )
        account = self.env['account.account'].browse(int(account_id))
        if not account.code.startswith(('6', '7')):
            values['analytic_distribution'] = None

        return values

    def _is_compatible_account(self):
        self.ensure_one()
        return (
                self.move_id.is_purchase_document()
                and
                self.account_id.account_type in ('expense', 'expense_depreciation', 'expense_direct_cost', 'income', 'income_other')
        ) or (
                self.move_id.is_sale_document()
                and
                self.account_id.account_type in ('income', 'income_other')
        )


class DeferredReportCustomHandler(models.AbstractModel):
    _inherit = 'account.deferred.report.handler'

    def _get_domain(self, report, options, filter_already_generated=False, filter_not_started=False):
        domain = report._get_options_domain(options, "from_beginning")
        account_types = ('expense', 'expense_depreciation', 'expense_direct_cost', 'income', 'income_other') if self._get_deferred_report_type() == 'expense' else ('income', 'income_other')
        domain += [
            ('account_id.account_type', 'in', account_types),
            ('deferred_start_date', '!=', False),
            ('deferred_end_date', '!=', False),
            ('deferred_end_date', '>=', options['date']['date_from']),
            ('move_id.date', '<=', options['date']['date_to']),
        ]
        domain += [  # Exclude if entirely inside the period
            '!', '&', '&', '&', '&', '&',
            ('deferred_start_date', '>=', options['date']['date_from']),
            ('deferred_start_date', '<=', options['date']['date_to']),
            ('deferred_end_date', '>=', options['date']['date_from']),
            ('deferred_end_date', '<=', options['date']['date_to']),
            ('move_id.date', '>=', options['date']['date_from']),
            ('move_id.date', '<=', options['date']['date_to']),
        ]
        if filter_already_generated:
            domain += [
                ('deferred_end_date', '>=', options['date']['date_from']),
                '!',
                    '&',
                    ('move_id.deferred_move_ids.date', '=', options['date']['date_to']),
                    ('move_id.deferred_move_ids.state', '=', 'posted'),
            ]
        if filter_not_started:
            domain += [('deferred_start_date', '>', options['date']['date_to'])]
        return domain