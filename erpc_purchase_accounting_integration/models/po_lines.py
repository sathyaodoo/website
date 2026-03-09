import json
import logging
from markupsafe import Markup
from odoo import models, fields, api, _
from odoo.tools import formatLang, format_date, plaintext2html
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    po_reference = fields.Char(related="order_id.name", string="PO Source Document", store=True, readonly=True)
    erpc_date_approve = fields.Datetime(related="date_approve", string="Confirmation Date", store=True, readonly=True)

    store_related_requisition_line_name = fields.Many2one(
        comodel_name="purchase.requisition",
        string="BO Ref",
        related="related_requisition_line_id.requisition_id",
        store=True,
        readonly=True
    )

    bo_origin = fields.Char(
        related="related_requisition_line_id.requisition_id.origin",
        string="BO Source Document",
        store=True,
        readonly=True
    )
    bo_order_date = fields.Date(related='related_requisition_line_name.ordering_date', string='BO Order Date',
                                store=True, readonly=True)
    receipt_date = fields.Datetime(related='order_id.effective_date', string='Receipt Date', store=True, readonly=True)

    invoice_payments_widget = fields.Binary(
        groups="account.group_account_invoice,account.group_account_readonly",
        compute='_compute_payments_widget_pol_reconciled_info',
        string="Bill Payments",
        exportable=False,
    )
    invoice_payments_text = fields.Text(
        compute='_compute_payments_widget_pol_reconciled_info',
        string="Bill Payments",
        exportable=True,
    )

    # @api.depends('invoice_lines.move_id.move_type', 'invoice_lines.move_id.line_ids.amount_residual',
    #              'invoice_lines.move_id.payment_state')
    # def _compute_payments_widget_pol_reconciled_info(self):
    #     for pol in self:
    #         pol_invoice_lines = pol.invoice_lines.filtered(
    #             lambda l: l.parent_state == 'posted' and l.move_id.payment_state not in ["not_paid",
    #                                                                                      "invoicing_legacy"])
    #         bill_ids = pol_invoice_lines.mapped('move_id')
    #         _logger.info(f'\n\n\n\n*****bill_ids***_compute_payments_widget_pol_reconciled_info****{bill_ids}\n\n\n\n.')
    #         payments_widget_vals = {'content': []}
    #         for move in bill_ids:
    #             payments_widget_vals = {'content': []}
    #             if move.state == 'posted' and move.is_invoice(include_receipts=True):
    #                 reconciled_vals = []
    #                 reconciled_partials = move.sudo()._get_all_reconciled_invoice_partials()
    #                 for reconciled_partial in reconciled_partials:
    #                     counterpart_line = reconciled_partial['aml']
    #                     if counterpart_line.move_id.ref:
    #                         reconciliation_ref = '%s (%s)' % (
    #                         counterpart_line.move_id.name, counterpart_line.move_id.ref)
    #                     else:
    #                         reconciliation_ref = counterpart_line.move_id.name
    #                     if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
    #                         foreign_currency = counterpart_line.currency_id
    #                     else:
    #                         foreign_currency = False
    #
    #                     reconciled_vals.append({
    #                         'amount': reconciled_partial['amount'],
    #                         'currency_id': move.company_id.currency_id.id if reconciled_partial['is_exchange'] else
    #                         reconciled_partial['currency'].id,
    #                         'date': counterpart_line.date,
    #                         'ref': reconciliation_ref,
    #                         # 'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance),
    #                         #                                       currency_obj=counterpart_line.company_id.currency_id),
    #                         # 'amount_foreign_currency': foreign_currency and formatLang(self.env,
    #                         #                                                            abs(counterpart_line.amount_currency),
    #                         #                                                            currency_obj=foreign_currency)
    #                     })
    #                 payments_widget_vals['content'] = reconciled_vals
    #
    #         if payments_widget_vals['content']:
    #             pol.invoice_payments_widget = payments_widget_vals
    #         else:
    #             pol.invoice_payments_widget = False

    @api.depends('invoice_lines.move_id.move_type', 'invoice_lines.move_id.line_ids.amount_residual',
                 'invoice_lines.move_id.payment_state')
    def _compute_payments_widget_pol_reconciled_info(self):
        for pol in self:
            pol_invoice_lines = pol.invoice_lines.filtered(
                lambda l: l.parent_state == 'posted' and l.move_id.payment_state not in ["not_paid",
                                                                                         "invoicing_legacy"])
            bill_ids = pol_invoice_lines.mapped('move_id')
            _logger.info(f'\n\n\n\n*****bill_ids***_compute_payments_widget_pol_reconciled_info****{bill_ids}\n\n\n\n.')
            payments_widget_vals = {'content': []}
            for move in bill_ids:
                payments_widget_vals = {'content': []}
                if move.state == 'posted' and move.is_invoice(include_receipts=True):
                    reconciled_vals = []
                    reconciled_partials = move.sudo()._get_all_reconciled_invoice_partials()
                    for reconciled_partial in reconciled_partials:
                        counterpart_line = reconciled_partial['aml']
                        if counterpart_line.move_id.ref:
                            reconciliation_ref = '%s (%s)' % (
                                counterpart_line.move_id.name, counterpart_line.move_id.ref)
                        else:
                            reconciliation_ref = counterpart_line.move_id.name
                        if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
                            foreign_currency = counterpart_line.currency_id
                        else:
                            foreign_currency = False

                        reconciled_vals.append({
                            'amount': reconciled_partial['amount'],
                            'currency_id': move.company_id.currency_id.id if reconciled_partial['is_exchange'] else
                            reconciled_partial['currency'].id,
                            'date': counterpart_line.date,
                            'ref': reconciliation_ref,
                            'is_exchange': reconciled_partial['is_exchange'],
                            # 'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance),
                            #                                       currency_obj=counterpart_line.company_id.currency_id),
                            # 'amount_foreign_currency': foreign_currency and formatLang(self.env,
                            #                                                            abs(counterpart_line.amount_currency),
                            #                                                            currency_obj=foreign_currency)
                        })
                    payments_widget_vals['content'] = reconciled_vals

            if payments_widget_vals['content']:
                pol.invoice_payments_widget = payments_widget_vals
            else:
                pol.invoice_payments_widget = False

            payments_vals = payments_widget_vals['content']

            # invoice_payments_text = ''
            # for pay_val in payments_vals:
            #     if not pay_val['is_exchange']:
            #         currency_id = pay_val['currency_id']
            #         pay_text = 'Paid on | %s %s%s' % (
            #             pay_val['date'], pay_val['amount'], currency_id.symbol)
            #         invoice_payments_text += plaintext2html(pay_text)
            #         invoice_payments_text += Markup('<br/>')
            # pol.invoice_payments_text = invoice_payments_text
            lines = []
            for p in payments_vals:
                if p.get('is_exchange'):
                    continue
                cur = self.env['res.currency'].browse(p['currency_id'])  # ID -> record
                amt = formatLang(self.env, p['amount'], currency_obj=cur)
                d = format_date(self.env, p['date'])
                lines.append(_("Paid on %s %s") % (d, amt))

            pol.invoice_payments_text = "\n".join(lines) if lines else False

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'price_unit' in fields:
            fields.remove('price_unit')
        return super(PurchaseOrderLine, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                           orderby=orderby, lazy=lazy)
