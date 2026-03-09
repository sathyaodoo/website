from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    numerical_sequence = fields.Char("Numerical Sequence")

    # @api.depends('name')
    # def _compute_numerical_sequence(self):
    #     for invoice in self:
    #         invoice.numerical_sequence = ''.join(filter(str.isdigit, invoice.name))

    @api.onchange('partner_id')
    def _compute_numerical_sequence(self):
        for invoice in self:
            if invoice.name:
                invoice.numerical_sequence = ''.join(filter(str.isdigit, invoice.name))
            else:
                invoice.numerical_sequence = False

    def action_post(self):
        res = super(AccountInvoice, self).action_post()
        self._compute_numerical_sequence()
        return res

    @api.onchange('move_type')
    def _compute_journal_id(self):
        for record in self:
            if record.move_type == 'in_invoice' and record.journal_id != False and not self._context.get('create_from_po'):
                record.journal_id = False
            else:
                super(AccountInvoice, self)._compute_journal_id()

    @api.depends('journal_id', 'statement_line_id')
    def _compute_currency_id(self):
        for invoice in self:
            currency = (
                    invoice.statement_line_id.foreign_currency_id
                    or invoice.journal_id.currency_id
                    or invoice.currency_id
                    or invoice.journal_id.company_id.currency_id
                    or invoice.company_id.currency_id
            )
            invoice.currency_id = currency


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_create_invoice(self):
        invoices = super(PurchaseOrder, self.with_context(create_from_po=True)).action_create_invoice()
        return invoices