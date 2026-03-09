from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    is_foreign_purchase_bill = fields.Boolean(copy=False, readonly=True)
    transfer_bill_entry = fields.Many2one('account.move', string="Transfer Bill Entry", copy=False, )
    transfer_bill_entry_count = fields.Integer(
        string="Transfer Bill Entry Count",
        compute="_compute_transfer_bill_entry_count",
        store=False
    )

    @api.depends('transfer_bill_entry')
    def _compute_transfer_bill_entry_count(self):
        for move in self:
            move.transfer_bill_entry_count = 1 if move.transfer_bill_entry else 0

    def action_view_transfer_bill_entry(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Transfer Bill Entry'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.transfer_bill_entry.id,
            'target': 'current',
        }

    def action_post(self):
        for move in self:
            if move.journal_id == move.company_id.foreign_purchase_journal_id:
                _logger.info(
                    f"\n\n\n\n ****action_post**foreign purchase** {move.journal_id, move.company_id.foreign_purchase_journal_id}")
                move.update({'is_foreign_purchase_bill': True, })
                _logger.info(
                    f"\n\n\n\n action_post update {move.is_foreign_purchase_bill, move.company_id.foreign_purchase_journal_id}")
        return super().action_post()

    @api.onchange('is_foreign_purchase_bill')
    def _onchange_is_foreign_purchase_bill(self):
        for move in self:
            if move.is_foreign_purchase_bill and move.move_type == 'in_invoice':
                _logger.info(
                    f"\n\n\n\n default bill accounts {move.company_id.foreign_purchase_journal_id, move.company_id.foreign_account_id, move.company_id.foreign_purchase_account_id}")
                if not move.company_id.foreign_purchase_journal_id:
                    raise UserError(_(
                        "You should configure the 'Foreign Purchase Journal' in your company settings."
                    ))
                if not move.company_id.foreign_account_id or not move.company_id.foreign_purchase_account_id:
                    raise UserError(_(
                        "You should configure the 'Foreign Account/Fooreign Purchase Account' in your company settings."
                    ))
                if move.journal_id == move.company_id.foreign_purchase_journal_id:
                    for line in move.invoice_line_ids:
                        _logger.info(
                            f"\n\n\n\n line_account {line.account_id, line.move_id.company_id.foreign_purchase_account_id}")
                        if line.account_id == line.move_id.company_id.foreign_purchase_account_id:
                            line.account_id = line.move_id.company_id.foreign_account_id.id
                            line.analytic_distribution = None

    def write(self, vals):
        # Check if the checkbox is ticked during save
        for move in self:
            if vals.get('is_foreign_purchase_bill') and move.move_type == 'in_invoice':
                if move.journal_id == move.company_id.foreign_purchase_journal_id:
                    for line in move.invoice_line_ids:
                        if line.account_id == line.move_id.company_id.foreign_purchase_account_id:
                            line.account_id = line.move_id.company_id.foreign_account_id
                            line.analytic_distribution = None
        return super(AccountMove, self).write(vals)

    def create_foreign_purchase_entry(self):
        for move in self:
            if not move.company_id.foreign_purchase_journal_id or \
                    not move.company_id.foreign_journal_id or \
                    not move.company_id.foreign_account_id or \
                    not move.company_id.foreign_purchase_account_id:
                raise UserError(_("Please configure the 'Foreign Purchase Journal', 'Foreign Account', "
                                  "and 'Foreign Purchase Account' in the company settings."))

            journal = move.company_id.foreign_journal_id
            lines_to_reverse = move.invoice_line_ids.filtered(
                lambda l: l.account_id == move.company_id.foreign_account_id
            )
            # total_amount = sum(lines_to_reverse.mapped('price_total'))

            # Compute line values
            move_lines = []
            # move_lines = [
            #     # Line for account 2 (Foreign Account)
            #     (0, 0, {
            #         'account_id': move.company_id.foreign_account_id.id,
            #         'debit': 0.0,
            #         'credit': total_amount,
            #         'partner_id': move.partner_id.id,
            #         'name': _('Transfer for %s') % move.name,
            #     }),
            #     # Line for account 1 (Foreign Purchase Account)
            #     (0, 0, {
            #         'account_id': move.company_id.foreign_purchase_account_id.id,
            #         'debit': total_amount,
            #         'credit': 0.0,
            #         'partner_id': move.partner_id.id,
            #         'name': _('Transfer for %s') % move.name,
            #     }),
            # ]
            for line in lines_to_reverse:
                amount = line.price_total
                currency_id = line.currency_id
                date = fields.Date.context_today(self)
                balance = line.currency_id._convert(amount, line.company_id.currency_id, line.company_id, date)
                move_lines.append((0, 0, {
                    'account_id': move.company_id.foreign_account_id.id,
                    'amount_currency': -amount,
                    'currency_id': currency_id.id,
                    'debit': 0.0,
                    'credit': balance,
                    'partner_id': move.partner_id.id,
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'expected_arrival_date': line.expected_arrival_date,
                }))
                move_lines.append((0, 0, {
                    'account_id': move.company_id.foreign_purchase_account_id.id,
                    'amount_currency': amount,
                    'currency_id': currency_id.id,
                    'debit': balance,
                    'credit': 0.0,
                    'partner_id': move.partner_id.id,
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'expected_arrival_date': line.expected_arrival_date,
                }))

            # Create the journal entry
            new_move = self.env['account.move'].create({
                'move_type': 'entry',
                'journal_id': journal.id,
                # 'date': move.date,
                'date': fields.Date.context_today(self),
                'landed_costs_show': True,
                'invoice_origin': move.name,
                'ref': _('Transfer for %s') % move.name,
                'line_ids': move_lines,
            })
            move.transfer_bill_entry = new_move.id
            move.transfer_bill_entry._post(soft=True)

    def button_cancel(self):
        res = super().button_cancel()
        for rec in self:
            if rec.transfer_bill_entry and rec.transfer_bill_entry.state != 'cancel':
                rec.transfer_bill_entry.button_cancel()
        return res

    def button_draft(self):
        res = super().button_draft()
        for rec in self:
            if rec.transfer_bill_entry and rec.transfer_bill_entry.state != 'draft':
                rec.transfer_bill_entry.button_draft()
        return res

    # def action_post(self):
    #     res = super().action_post()
    #     for rec in self:
    #         if rec.transfer_bill_entry and rec.transfer_bill_entry.state != 'posted':
    #             rec.transfer_bill_entry.action_post()
    #     return res
