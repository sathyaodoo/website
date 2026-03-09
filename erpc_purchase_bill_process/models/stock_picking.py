from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        picking = super().button_validate()
        for stock in self:
            if stock.purchase_id:
                _logger.info(
                    f"\n\n\n\n stock.purchase_id {stock.purchase_id}")
                if stock.purchase_id.invoice_ids:
                    for bill in stock.purchase_id.invoice_ids:
                        _logger.info(
                            f"\n\n\n\n stock.purchase_id.invoice_ids {stock.purchase_id.invoice_ids}")
                        if not bill.transfer_bill_entry and bill.is_foreign_purchase_bill and bill.state == 'posted':
                            bill.create_foreign_purchase_entry()
                            _logger.info(
                                f"\n\n\n\n stock.purchase_id.invoice_ids.transfer_bill_entry {bill.transfer_bill_entry}")
                            if bill.transfer_bill_entry:
                                initial_bill_lines = bill.invoice_line_ids.filtered(
                                    lambda
                                        l: l.account_id.reconcile and not l.reconciled and l.account_type != 'liability_payable' and l.parent_state == 'posted'
                                )
                                lines_to_reconcile = bill.transfer_bill_entry.line_ids.filtered(
                                    lambda
                                        l: l.account_id.reconcile and not l.reconciled and l.account_type != 'liability_payable' and l.parent_state == 'posted'
                                )
                                if lines_to_reconcile and initial_bill_lines:
                                    for bill_line in initial_bill_lines:

                                        for entry_line in lines_to_reconcile:
                                            if (
                                                    entry_line.account_id == bill_line.account_id
                                                    and entry_line.partner_id == bill_line.partner_id
                                                    and not bill_line.reconciled
                                                    and not entry_line.reconciled
                                                    and bill_line.balance * entry_line.balance < 0
                                                    and abs(bill_line.amount_currency) == abs(entry_line.amount_currency)
                                            ):
                                                (bill_line + entry_line).reconcile()
                                                break

        return picking
