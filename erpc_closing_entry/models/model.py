from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

logger = logging.getLogger(__name__)


# Add this class to extend account.account model
class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_regulatory_account = fields.Boolean(
        string='Is Regulatory Account',
        default=False,
        help='If checked, this account will be used as regulatory account for closing entries'
    )


class ClosingEntryLine(models.TransientModel):
    _name = 'closing.entry.line'
    _description = 'Internal Transfer Line'

    wizard_id = fields.Many2one('closing.entry.wizard', string='Wizard')
    group_account = fields.Many2one('account.account', string='Group of Account', required=True)
    debit_credit_account = fields.Many2one('account.account', string='Debit/Credit Account', required=True)
    partner_id = fields.Many2one('res.partner', string='Settlement Partner')  # NEW FIELD ADDED AT LINE LEVEL


class ClosingEntry(models.TransientModel):
    _name = 'closing.entry.wizard'
    _description = 'Internal Transfer Wizard'

    journal_date = fields.Date(string='Journal Date', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    regulatory_account_id = fields.Many2one(
        'account.account',
        string='Regulatory Account',
        default=lambda self: self._default_regulatory_account_id()
    )
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    line_ids = fields.One2many('closing.entry.line', 'wizard_id', string='Lines')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    move_id = fields.Many2one('account.move', string='Journal Entry')

    def _default_regulatory_account_id(self):
        """Default method to get the regulatory account"""
        regulatory_account = self.env['account.account'].search([
            ('is_regulatory_account', '=', True),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        return regulatory_account.id if regulatory_account else False

    def action_confirm(self):
        self.ensure_one()

        # Create journal entry lines
        move_lines = []
        processed_accounts = set()

        # Check if wizard currency matches company currencies
        is_main_currency = self.currency_id == self.company_id.currency_id
        is_second_currency = self.currency_id == self.company_id.second_currency

        for line in self.line_ids:
            # Skip if we've already processed this account
            if line.group_account.id in processed_accounts:
                continue

            processed_accounts.add(line.group_account.id)

            # Find all move lines for this account in the period
            domain = [
                ('account_id', '=', line.group_account.id),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('company_id', '=', self.company_id.id),
                ('parent_state', '=', 'posted')
            ]

            move_lines_found = self.env['account.move.line'].search(domain)

            if not move_lines_found:
                logger.info(f"No move lines found for account {line.group_account.display_name}")
                continue

            # Group by partner and currency and calculate total balance
            groups = {}
            for ml in move_lines_found:
                key = (ml.partner_id.id or False, ml.currency_id.id or False)
                if key not in groups:
                    groups[key] = {
                        'partner': ml.partner_id,
                        'currency': ml.currency_id,
                        'balance': 0.0,
                        'amount_currency': 0.0,
                        'second_balance': 0.0,
                        'third_balance': 0.0
                    }

                # Sum the balances for all currencies
                groups[key]['balance'] += ml.balance
                groups[key]['amount_currency'] += ml.amount_currency
                groups[key]['second_balance'] += ml.second_balance
                groups[key]['third_balance'] += ml.third_balance

            logger.info(f"Groups for account {line.group_account.display_name}: {groups}")

            # Create adjustment entries for each group
            for key, group_data in groups.items():
                balance = group_data['balance']
                amount_currency = group_data['amount_currency']
                second_balance = group_data['second_balance']
                third_balance = group_data['third_balance']

                if balance == 0 and second_balance == 0 and third_balance == 0:
                    continue

                # Get the original currency for group_account and wizard currency for settlement accounts
                original_currency = group_data['currency'] or self.currency_id
                wizard_currency = self.currency_id

                # Calculate amount_currency for settlement accounts
                if is_main_currency:
                    # If wizard currency is the company's main currency, use balance for amount_currency
                    settlement_amount_currency = balance
                elif is_second_currency:
                    # If wizard currency is the company's second currency, use second_balance for amount_currency
                    settlement_amount_currency = second_balance
                else:
                    # Original logic for other currencies
                    if original_currency != wizard_currency:
                        # Convert the amount from original currency to wizard currency
                        settlement_amount_currency = original_currency._convert(
                            abs(amount_currency) if amount_currency != 0 else abs(balance),
                            wizard_currency,
                            self.company_id,
                            self.journal_date or fields.Date.today()
                        )
                        # Apply the correct sign
                        if (balance < 0 and amount_currency < 0) or (balance > 0 and amount_currency > 0):
                            settlement_amount_currency = abs(settlement_amount_currency)
                        else:
                            settlement_amount_currency = -abs(settlement_amount_currency)
                    else:
                        # Same currency, use the original amount_currency
                        settlement_amount_currency = amount_currency

                # Determine settlement partner: use line partner if set, otherwise use VAT line partner
                settlement_partner = line.partner_id if line.partner_id else group_data[
                    'partner']  # CHANGED: Use line.partner_id

                # Create debit/credit lines based on balance
                if balance < 0:
                    # Negative balance: Create debit line to zero out (group_account keeps original currency)
                    move_lines.append((0, 0, {
                        'account_id': line.group_account.id,
                        'partner_id': group_data['partner'].id,
                        'currency_id': original_currency.id,
                        'name': _('VAT Closing Adjustment'),
                        'debit': abs(balance),
                        'credit': 0,
                        'amount_currency': abs(amount_currency) if amount_currency < 0 else -abs(amount_currency),
                        'second_debit_id': abs(second_balance) if second_balance < 0 else 0,
                        'second_credit_id': 0,
                        'third_debit_id': abs(third_balance) if third_balance < 0 else 0,
                        'third_credit_id': 0,
                    }))
                    # Credit line to settlement account (uses wizard currency)
                    move_lines.append((0, 0, {
                        'account_id': line.debit_credit_account.id,
                        'partner_id': settlement_partner.id,  # CHANGED: Use settlement_partner
                        'currency_id': wizard_currency.id,
                        'name': _('VAT Settlement'),
                        'debit': 0,
                        'credit': abs(balance),
                        'amount_currency': -abs(settlement_amount_currency) if settlement_amount_currency != 0 else 0,
                        'second_debit_id': 0,
                        'second_credit_id': abs(second_balance) if second_balance < 0 else 0,
                        'third_debit_id': 0,
                        'third_credit_id': abs(third_balance) if third_balance < 0 else 0,
                    }))
                else:
                    # Positive balance: Create credit line to zero out (group_account keeps original currency)
                    move_lines.append((0, 0, {
                        'account_id': line.group_account.id,
                        'partner_id': group_data['partner'].id,
                        'currency_id': original_currency.id,
                        'name': _('VAT Closing Adjustment'),
                        'debit': 0,
                        'credit': balance,
                        'amount_currency': -abs(amount_currency) if amount_currency > 0 else abs(amount_currency),
                        'second_debit_id': 0,
                        'second_credit_id': abs(second_balance) if second_balance > 0 else 0,
                        'third_debit_id': 0,
                        'third_credit_id': abs(third_balance) if third_balance > 0 else 0,
                    }))
                    # Debit line to settlement account (uses wizard currency)
                    move_lines.append((0, 0, {
                        'account_id': line.debit_credit_account.id,
                        'partner_id': settlement_partner.id,  # CHANGED: Use settlement_partner
                        'currency_id': wizard_currency.id,
                        'name': _('VAT Settlement'),
                        'debit': balance,
                        'credit': 0,
                        'amount_currency': abs(settlement_amount_currency) if settlement_amount_currency != 0 else 0,
                        'second_debit_id': abs(second_balance) if second_balance > 0 else 0,
                        'second_credit_id': 0,
                        'third_debit_id': abs(third_balance) if third_balance > 0 else 0,
                        'third_credit_id': 0,
                    }))

        if not move_lines:
            raise UserError(_('No adjustments to make for the selected period and accounts.'))

        # Create the journal entry
        move_vals = {
            'date': self.journal_date,
            'ref': _('VAT Closing %s to %s') % (self.date_from, self.date_to),
            'journal_id': self.journal_id.id,
            'line_ids': move_lines,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
        }

        # Set multi-currency fields if company has multi-currency enabled
        if self.company_id.multi_currency:
            move_vals.update({
                'multi_currency': True,
                'second_currency': self.company_id.second_currency.id,
                'third_currency': self.company_id.third_currency.id,
            })

        self.move_id = self.env['account.move'].create(move_vals)

        # Post the journal entry automatically
        self.move_id.action_post()

        # Return action to view the created journal entry
        return {
            'name': _('Journal Entry'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.move_id.id,
            'target': 'current',
        }