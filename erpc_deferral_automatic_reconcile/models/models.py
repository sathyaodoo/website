from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        posted = super()._post(soft)
        for move in self:
            if move.deferred_original_move_ids:
                _logger.info(f"\n\n\n\n\n\n move _post {move.id}")
                move._automated_reconcile_deferral()
        return posted

    def _automated_reconcile_deferral(self):
        """
        Reconcile the deferred entries for the invoice.
        """
        self.ensure_one()
        initial_entry_lines = self.line_ids.filtered(
            lambda l: l.account_id.reconcile and not l.reconciled and l.move_type == 'entry' and l.parent_state == 'posted'
        )
        _logger.info(f"\n\n\n\n\n\n initial_entry_lines _automated_reconcile_deferral {initial_entry_lines}")
        deferral_lines = self.env['account.move.line'].search([
            ('move_id.deferred_original_move_ids', 'in', self.deferred_original_move_ids.ids),
            ('account_id.reconcile', '=', True),
            ('reconciled', '=', False),
            ('parent_state', '=', 'posted'),  # Ensure the partner matches
        ])
        _logger.info(f"\n\n\n\n\n\n deferral_lines _automated_reconcile_deferral {deferral_lines}")
        for initial_line in initial_entry_lines:
            _logger.info(f"\n\n\n\n\n\n initial_line _automated_reconcile_deferral {initial_line.parent_state}")
            matching_lines = self.env['account.move.line']

            for deferral_line in deferral_lines:
                _logger.info(f"\n\n\n\n\n\n deferral_line _automated_reconcile_deferral {deferral_line.parent_state}")
                if (deferral_line.account_id == initial_line.account_id and
                        deferral_line.partner_id == initial_line.partner_id and
                        initial_line.balance * deferral_line.balance < 0):

                    matching_lines += deferral_line

                    if not deferral_line.reconciled:
                        (matching_lines + initial_line).reconcile()
                        break
