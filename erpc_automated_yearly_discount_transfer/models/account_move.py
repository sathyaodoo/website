from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    transfer_deferral_yearly_entry = fields.Many2one('account.move', string="Transfer Deferral Yearly Entry", copy=False, )
    transfer_deferral_yearly_entry_count = fields.Integer(
        string="Transfer Deferral Yearly Entry Count",
        compute="_compute_transfer_deferral_yearly_entry_count",
        store=False
    )

    @api.depends('transfer_deferral_yearly_entry')
    def _compute_transfer_deferral_yearly_entry_count(self):
        for move in self:
            move.transfer_deferral_yearly_entry_count = 1 if move.transfer_deferral_yearly_entry else 0

    def action_view_transfer_yearly_entry(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Transfer Deferral Yearly Discount Entry'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.transfer_deferral_yearly_entry.id,
            'target': 'current',
        }

    def action_post(self):
        for move in self:
            if move.journal_id == move.company_id.yearly_discount_journal_id:
                move.create_transfer_yearly_entry()
        return super().action_post()

    def create_transfer_yearly_entry(self):
        for move in self:
            if not move.company_id.internal_transfer_journal_id or \
                    not move.company_id.deferral_payable_account_id or \
                    not move.company_id.deferral_receivable_account_id:
                raise UserError(_("Please configure the 'Internal Transfer Journal', "
                                  "'Deferral Payable Account' and 'Deferral Receivable Account' in the company"
                                  " settings."))

            journal = move.company_id.internal_transfer_journal_id
            lines_to_transfer = move.line_ids.filtered(
                lambda l: l.account_id == move.company_id.deferral_payable_account_id
            )

            move_lines = []
            for line in lines_to_transfer:
                amount = line.amount_currency
                currency_id = line.currency_id
                date = move.date
                balance = line.currency_id._convert(amount, line.company_id.currency_id, line.company_id, date)
                move_lines.append((0, 0, {
                    'account_id': move.company_id.deferral_payable_account_id.id,
                    'amount_currency': -amount,
                    'currency_id': currency_id.id,
                    'debit': abs(balance) if amount < 0 else 0,
                    'credit': abs(balance) if amount > 0 else 0,
                    'partner_id': move.partner_id.id,
                    'name': line.name,
                }))
                move_lines.append((0, 0, {
                    'account_id': move.company_id.deferral_receivable_account_id.id,
                    'amount_currency': amount,
                    'currency_id': currency_id.id,
                    'debit': abs(balance) if amount > 0 else 0,
                    'credit': abs(balance) if amount < 0 else 0,
                    'partner_id': move.partner_id.id,
                    'name': line.name,
                }))

            # Create the journal entry
            new_move = self.env['account.move'].create({
                'move_type': 'entry',
                'journal_id': journal.id,
                'date': date,
                'invoice_origin': move.name,
                'ref': _('Transfer Yearly Discount for %s') % move.name,
                'line_ids': move_lines,
            })
            move.transfer_deferral_yearly_entry = new_move.id
            move.transfer_deferral_yearly_entry._post(soft=True)

    def button_draft(self):
        res = super().button_draft()
        for rec in self:
            if rec.transfer_deferral_yearly_entry and rec.transfer_deferral_yearly_entry.state != 'draft':
                rec.transfer_deferral_yearly_entry.button_draft()
                rec.transfer_deferral_yearly_entry.unlink()
        return res


