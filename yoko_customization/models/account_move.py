from collections import defaultdict

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, AccessError, MissingError
from datetime import datetime, timedelta
from odoo.exceptions import UserError

import json
import logging

from odoo.tools import formatLang

logger = logging.getLogger(__name__)


# class AccountTax(models.Model):
#     _inherit = "account.tax"
#
#     def _prepare_tax_totals(self, base_lines, currency, tax_lines=None, is_credit_note=False,
#                             is_company_currency_requested=False):
#
#         to_process = []
#         for base_line in base_lines:
#             if base_line.get('quantity') == 0 and is_credit_note == True:
#                 base_line['quantity'] = 1
#             to_update_vals, tax_values_list = self._compute_taxes_for_single_line(base_line)
#             to_process.append((base_line, to_update_vals, tax_values_list))
#
#         def grouping_key_generator(base_line, tax_values):
#             source_tax = tax_values['tax_repartition_line'].tax_id
#             return {'tax_group': source_tax.tax_group_id}
#
#         global_tax_details = self._aggregate_taxes(to_process, grouping_key_generator=grouping_key_generator)
#
#         tax_group_vals_list = []
#         for tax_detail in global_tax_details['tax_details'].values():
#             tax_group_vals = {
#                 'tax_group': tax_detail['tax_group'],
#                 'base_amount': tax_detail['base_amount_currency'],
#                 'tax_amount': tax_detail['tax_amount_currency'],
#             }
#             if is_company_currency_requested:
#                 tax_group_vals['base_amount_company_currency'] = tax_detail['base_amount']
#                 tax_group_vals['tax_amount_company_currency'] = tax_detail['tax_amount']
#
#             # Handle a manual edition of tax lines.
#             if tax_lines is not None:
#                 matched_tax_lines = [
#                     x
#                     for x in tax_lines
#                     if x['tax_repartition_line'].tax_id.tax_group_id == tax_detail['tax_group']
#                 ]
#                 if matched_tax_lines:
#                     tax_group_vals['tax_amount'] = sum(x['tax_amount'] for x in matched_tax_lines)
#
#             tax_group_vals_list.append(tax_group_vals)
#
#         tax_group_vals_list = sorted(tax_group_vals_list, key=lambda x: (x['tax_group'].sequence, x['tax_group'].id))
#
#         # ==== Partition the tax group values by subtotals ====
#
#         amount_untaxed = global_tax_details['base_amount_currency']
#         amount_tax = 0.0
#
#         amount_untaxed_company_currency = global_tax_details['base_amount']
#         amount_tax_company_currency = 0.0
#
#         subtotal_order = {}
#         groups_by_subtotal = defaultdict(list)
#         for tax_group_vals in tax_group_vals_list:
#             tax_group = tax_group_vals['tax_group']
#
#             subtotal_title = tax_group.preceding_subtotal or _("Untaxed Amount")
#             sequence = tax_group.sequence
#
#             subtotal_order[subtotal_title] = min(subtotal_order.get(subtotal_title, float('inf')), sequence)
#             groups_by_subtotal[subtotal_title].append({
#                 'group_key': tax_group.id,
#                 'tax_group_id': tax_group.id,
#                 'tax_group_name': tax_group.name,
#                 'tax_group_amount': tax_group_vals['tax_amount'],
#                 'tax_group_base_amount': tax_group_vals['base_amount'],
#                 'formatted_tax_group_amount': formatLang(self.env, tax_group_vals['tax_amount'], currency_obj=currency),
#                 'formatted_tax_group_base_amount': formatLang(self.env, tax_group_vals['base_amount'],
#                                                               currency_obj=currency),
#             })
#             if is_company_currency_requested:
#                 groups_by_subtotal[subtotal_title][-1]['tax_group_amount_company_currency'] = tax_group_vals[
#                     'tax_amount_company_currency']
#                 groups_by_subtotal[subtotal_title][-1]['tax_group_base_amount_company_currency'] = tax_group_vals[
#                     'base_amount_company_currency']
#
#         # ==== Build the final result ====
#
#         subtotals = []
#         for subtotal_title in sorted(subtotal_order.keys(), key=lambda k: subtotal_order[k]):
#             amount_total = amount_untaxed + amount_tax
#             subtotals.append({
#                 'name': subtotal_title,
#                 'amount': amount_total,
#                 'formatted_amount': formatLang(self.env, amount_total, currency_obj=currency),
#             })
#             if is_company_currency_requested:
#                 subtotals[-1]['amount_company_currency'] = amount_untaxed_company_currency + amount_tax_company_currency
#                 amount_tax_company_currency += sum(
#                     x['tax_group_amount_company_currency'] for x in groups_by_subtotal[subtotal_title])
#
#             amount_tax += sum(x['tax_group_amount'] for x in groups_by_subtotal[subtotal_title])
#
#         amount_total = amount_untaxed + amount_tax
#
#         display_tax_base = (len(global_tax_details['tax_details']) == 1 and currency.compare_amounts(
#             tax_group_vals_list[0]['base_amount'], amount_untaxed) != 0) \
#                            or len(global_tax_details['tax_details']) > 1
#
#         return {
#             'amount_untaxed': currency.round(amount_untaxed) if currency else amount_untaxed,
#             'amount_total': currency.round(amount_total) if currency else amount_total,
#             'formatted_amount_total': formatLang(self.env, amount_total, currency_obj=currency),
#             'formatted_amount_untaxed': formatLang(self.env, amount_untaxed, currency_obj=currency),
#             'groups_by_subtotal': groups_by_subtotal,
#             'subtotals': subtotals,
#             'subtotals_order': sorted(subtotal_order.keys(), key=lambda k: subtotal_order[k]),
#             'display_tax_base': display_tax_base
#         }


class AccountMove(models.Model):
    _inherit = 'account.move'

    can_edit_discount = fields.Boolean(
        string='Can Edit Discount', compute="_compute_can_edit_discount",
        required=False)

    @api.depends('company_id')
    def _compute_can_edit_discount(self):

        for record in self:
            if self.env.user.has_group('erpc_product_size.group_user_invoice_discount_access'):
                record.can_edit_discount = True
            else:
                record.can_edit_discount = False

    total_due = fields.Monetary(related='partner_id.total_due', string="Balance Due",
                                currency_field='company_currency_id')
    due_draft_invoice = fields.Monetary(compute="_compute_due_old_current", string="Balance Due",
                                        currency_field='company_currency_id', store=True)
    due_confirm_invoice = fields.Monetary(compute="_compute_confirmed_invoice_new", string="copy of due at posted",
                                          currency_field='company_currency_id', store=True)
    is_reversed = fields.Boolean(string='Is Reversed', default=False)
    is_credit_note = fields.Boolean(string="Is Credit Note", default=False,
                                    help="this flag indicates that the invoice is considered a credit note if value is true")
    return_delivery = fields.Selection(string="Return Delivery", default='done',
                                       selection=[('done', 'Done'), ('back', 'Delivery Back')])
    parent_company_id = fields.Many2one('res.partner', string='Parent Company', domain="[('is_driver', '=', False)]",
                                        compute='_get_parent_ids', store=True)
    driver_id = fields.Many2one('res.partner', string="Driver", required=False, store=True, tracking=True,
                                domain="[('is_driver', '=', True), ('driver_state', '=', 'active')]")
    # TODO GR: to add compute method in another module bc it takes long loading time
    # driver_id = fields.Many2one(
    #     "res.partner",
    #     string="Driver",
    #     required=False, tracking=True,
    #     compute="_compute_driver_id",
    #     store=True
    # )


    # collector = fields.Many2one('res.partner', string='Collector', store=True, tracking=True)
    # collector = fields.Many2one('res.partner', string='Collector', compute='_compute_collector', store=True, tracking=True)
    #   = fields.Char(string='User collector', compute='_compute_collection_user')
    user_salesman = fields.Char(string='User Salesman', compute='_compute_salesman_user')
    warehouse_id = fields.Many2one("stock.warehouse")
    # delivery_date = fields.Datetime("Delivery Date")
    # delivery_term = fields.Selection([
    #     ('-1', 'No Delivery'),
    #     ('0', 'Immediate'),
    #     ('1', 'Today'),
    #     ('2', 'Tomorrow'),
    #     ('3', 'Later')], string="Delivery Term", default="")

    # invoice_from_sale = fields.Boolean(string='Comming from sale', compute='_comming_from_sale_order')
    # user_is_super = fields.Boolean(compute="_compute_super_check")

    # @api.depends()
    # def _compute_super_check(self):
    #     self.user_is_super = self.env.user.has_group("yoko_security_custom.super_user")

    # @api.depends('invoice_line_ids.sale_line_ids.order_id.picking_ids.driver_id')
    # def _compute_driver_id(self):
    #     for move in self:
    #         driver = False
    #         sale_orders = move.invoice_line_ids.sale_line_ids.order_id
    #         pickings = sale_orders.picking_ids.filtered(lambda p: p.driver_id)
    #
    #         if pickings:
    #             # Take first picking driver (or last, depends on your process)
    #             driver = pickings[0].driver_id
    #
    #         move.driver_id = driver

    @api.depends('partner_id')
    def _get_parent_ids(self):
        for rec in self:
            if rec.partner_id:
                rec.parent_company_id = rec.partner_id.parent_id

    # def _comming_from_sale_order(self):
    #     for line in self:
    #         sale_id = self.env['sale.order'].search([('name', '=', line.invoice_origin)])
    #         if sale_id:
    #             line.invoice_from_sale = True
    #         else:
    #             line.invoice_from_sale = False

    @api.onchange('parent_company_id')
    def onchange_parent_id(self):
        if self.partner_id:  # to prevent recomputing partner_company_id while nulling the partner_id
            self.partner_id = False
        if self.parent_company_id:
            return {
                'domain': {'partner_id': [('parent_id', '=', self.parent_company_id.id), ('is_driver', '=', False)]}}
        else:
            return {'domain': {'partner_id': [('is_driver', '=', False)]}}

    @api.depends('state')
    def _compute_confirmed_invoice_new(self):
        for rec in self:
            if not rec.payment_state == 'reversed' and rec.state == 'posted' and not rec.reversed_entry_id:
                rec.due_confirm_invoice = rec.total_due

    @api.constrains('state', 'reversed_entry_id')
    def _compute_after_reversal(self):
        for rec in self:
            if rec.reversed_entry_id:
                rec.reversed_entry_id.due_draft_invoice = rec.due_draft_invoice

    @api.onchange('invoice_line_ids')
    def invoice_amount_validation_state(self):
        if self._origin.amount_total != self.amount_total:
            old_amount = self._origin.amount_total
            new_amount = self.amount_total
            if old_amount and new_amount == 0:
                raise ValidationError('Invoice has an amount of 0 please adjust to continue')

    @api.depends('state')
    def _compute_due_old_current(self):
        for rec in self:
            if not rec.payment_state == 'reversed' and rec.state == 'draft' and not rec.reversed_entry_id:
                rec.due_draft_invoice = rec.total_due
            elif rec.payment_state == 'reversed' and rec.state == 'posted' and not rec.reversed_entry_id and rec.due_confirm_invoice:
                rec.due_draft_invoice = rec.due_confirm_invoice
            elif rec.reversed_entry_id:
                rec.due_draft_invoice = rec.reversed_entry_id.due_confirm_invoice

    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total))

    num_word = fields.Char(string=_("Amount In Words:"), compute='_compute_amount_in_word')

    discount_rate = fields.Float('Discount Rate', digits='Account',
                                 readonly=True)
    discount_pricelists = fields.Many2many('product.pricelist')
    # kaza_id = fields.Many2one('res.partner.kaza', related='partner_id.kaza_id', store=True)
    # city_id = fields.Many2one('res.partner.city', related='partner_id.city_id', store=True)
    state_id = fields.Many2one('res.country.state', related='partner_id.state_id', store=True)
    # customer_category_id = fields.Many2one('customer.category', related='partner_id.customer_category_id', store=True)
    total_qty = fields.Float(compute='_get_total_qty', string="Total Quantity",
                             help="Total quantities for all products")
    # price_and_discount_read = fields.Boolean(compute="_compute_price_and_discount_read")

    # @api.depends("user_id")
    # def _compute_price_and_discount_read(self):
    #     self.price_and_discount_read = not self.env.user.has_group("yoko_security_custom.discount")

    # @api.depends('partner_id.collection_type')
    # def _compute_collection_user(self):
    #     for move in self:
    #         if move.partner_id:
    #             move.user_collector = move.partner_id.collection_type
    #         else:
    #             move.user_collector = False

    def _get_default_second_currency_id(self):
        second_currency_id = self.env.ref('base.LBP')
        return second_currency_id if second_currency_id else None

    second_currency_id = fields.Many2one('res.currency', string='Second Currency', required=True, readonly=False,
                                         store=True,
                                         default=_get_default_second_currency_id)

    # # fields for Central Bank (central_name_of_field )  that you need to add fields in this area
    # central_bank_rate = fields.Float('Central Bank rate', copy=False)
    # central_amount_untaxed = fields.Monetary(string='Central Untaxed Amount', store=True, compute='_amount_rate_all',
    #                                          tracking=5)
    # central_amount_tax = fields.Monetary(string='Central Taxes', store=True, compute='_amount_rate_all')
    # central_amount_total = fields.Monetary(string='Central Total', store=True, compute='_amount_rate_all', tracking=4)
    # central_tax_totals_json = fields.Char(compute='_compute_rate_tax_totals_json')
    #
    # # fields for Central Bank (black_name_of_field )  that you need to add fields in this area
    #
    # black_market_rate = fields.Float('Black Market rate', copy=False)
    # black_amount_untaxed = fields.Monetary(string='Black Untaxed Amount', store=True, compute='_amount_rate_all',
    #                                        tracking=5)
    # black_amount_tax = fields.Monetary(string='Black Taxes', store=True, compute='_amount_rate_all')
    # black_amount_total = fields.Monetary(string='Black Total', store=True, compute='_amount_rate_all', tracking=4)
    # black_tax_totals_json = fields.Char(compute='_compute_rate_tax_totals_json')

    # rate_access = fields.Boolean(compute="_compute_access_for_rate")

    # @api.onchange("rate_access")
    # def _compute_access_for_rate(self):
    #     # instead of wrtiting a long conition like "user.has_group(blabla) or user.has(blabla)  or user.has(blabla)",  i thoght of this : determine if True in list
    #     accessabilty_list = [self.env.user.has_group("sales_team.group_sale_manager"),
    #                          self.env.user.has_group("base.group_erp_manager"),
    #                          self.env.user.has_group("base.group_system")]
    #     print("accessabilty_list")
    #     print(accessabilty_list)
    #     self.rate_access = True in accessabilty_list

    in_lbp_currency = fields.Boolean(compute="_detect_order_in_lbp_currency")

    @api.onchange("currency_id")
    def _detect_order_in_lbp_currency(self):
        lbp_curr = self.env['res.currency'].search([('name', 'in', ['LBP', 'BMR'])])
        if self.currency_id.id in lbp_curr.ids:
            self.in_lbp_currency = True
        else:
            self.in_lbp_currency = False

    def _get_BMR_rate(self):
        current_rate = self.env.ref('base.LBP')
        return current_rate.rate

    current_rate = fields.Float("LBP Rate", default=_get_BMR_rate)

    untaxed_custom_amount = fields.Monetary(currency_field='second_currency_id', tracking=5, store=True,
                                            compute="_compute_tax_and_untaxed", string="Untaxed LBP Amount")
    taxed_custom_amount = fields.Monetary(currency_field='second_currency_id', store=True,
                                          compute="_compute_tax_and_untaxed", string="VAT LBP")

    @api.depends('invoice_line_ids.price_unit', 'invoice_line_ids.quantity', 'current_rate', 'currency_id',
                 'amount_untaxed')
    def _compute_tax_and_untaxed(self):
        for rec in self:
            black_market_currency = self.env['res.currency'].search([('name', '=', 'BMR')])
            # untaxed_custom = rec.amount_untaxed * rec.black_market_currency.rate
            untaxed_custom = rec.amount_untaxed * rec.current_rate

            # To include EURO rate within the amount
            if rec.currency_id.name == "EUR":
                untaxed_custom = untaxed_custom * rec.currency_id.inverse_rate

            # In case of LBP, BMR Don not apply Conversion Rate, it is already applied
            if rec.currency_id.name in ['LBP', 'BMR']:
                taxed_custom_amount = rec.amount_tax
            else:  # Convert it first to primary currency(e.g USD)
                taxed_custom_amount = rec.amount_tax * rec.currency_id.inverse_rate * rec.second_currency_id.rate

            rec.update({
                'untaxed_custom_amount': untaxed_custom,
                'taxed_custom_amount': taxed_custom_amount
            })

    # @api.onchange('partner_id')
    # def _onchange_partner_id_discount_pricelist(self):
    #     pricelist = self.partner_id._origin.discount_ids.mapped('price_list_id')
    #     print("pricelist", pricelist, )
    #     if not pricelist:
    #         self.discount_pricelists = None
    #     self.discount_pricelists = pricelist

    @api.onchange('discount_rate')
    def onchange_discount_rate(self):
        for rec in self:
            for line in rec.line_ids:
                line.update({'discount_rate_line': rec.discount_rate})
                line._compute_totals()

    # override  _compute_amount odoo base account.move function to add discount
    @api.depends('line_ids.amount_currency', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id',
                 'currency_id', 'amount_total', 'amount_untaxed', 'line_ids.discount_rate_line')
    def _compute_tax_totals_json(self):
        """ Computed field used for custom widget's rendering.
            Only set on invoices.
        """
        for move in self:
            if not move.is_invoice(include_receipts=True):
                # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
                move.tax_totals_json = None
                continue

            tax_lines_data = move._prepare_tax_lines_data_for_totals_from_invoice()

            move.tax_totals_json = json.dumps({
                **self._get_tax_totals(move.partner_id, tax_lines_data, move.amount_total, move.amount_untaxed,
                                       move.currency_id),
                'allow_tax_edition': move.is_purchase_document(include_receipts=False) and move.state == 'draft',
            })

    @api.depends('invoice_line_ids', 'invoice_line_ids.quantity')
    def _get_total_qty(self):
        for rec in self:
            rec.total_qty = sum(rec.invoice_line_ids.mapped('quantity'))

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if 'current_rate' in vals:

            black_market_currency = self.env['res.currency'].search([('name', '=', 'BMR')])

            if black_market_currency:
                # black_market_currency.rate_ids.unlink()
                # self.env.cr.commit()
                today_rate = black_market_currency.rate_ids.filtered(lambda rate: rate.name == fields.Date.today())
                if not today_rate:  # if there is no rate for today, create a new one of today
                    currency_rate_model = self.env['res.currency.rate']
                    currency_rate_obj = currency_rate_model.create({
                        "currency_id": black_market_currency.id,
                        "name": fields.Datetime.now(),
                        "company_rate": vals.get("current_rate")
                    })
        return res

    @api.model_create_multi
    def create(self, vals):
        black_market_currency = self.env['res.currency'].search([('name', '=', 'BMR')])

        if not 'from_order' in vals:
            if "current_rate" in vals and vals.get("current_rate") > 0:
                black_market_currency = self.env['res.currency'].search([('name', '=', 'BMR')])
                if black_market_currency:
                    # black_market_currency.rate_ids.unlink()
                    # self.env.cr.commit()
                    today_rate = black_market_currency.rate_ids.filtered(lambda rate: rate.name == fields.Date.today())
                    if not today_rate:
                        currency_rate_model = self.env['res.currency.rate']
                        currency_rate_obj = currency_rate_model.create({
                            "currency_id": black_market_currency.id,
                            "name": fields.Datetime.now(),
                            "company_rate": vals.get("current_rate")
                        })
        else:
            # Handelling invalid field error because we send this field here from prepare invoice
            del vals['from_order']

        if self._context.get('credit_note', False):
            for v in vals:
                v['is_credit_note'] = True

        res = super(AccountMove, self).create(vals)

        return res

    # @api.onchange('currency_id')
    # def onchange_currency_id_rate(self):
    #     for rec in self:
    #         rec.central_bank_rate = rec.currency_id.central_bank_rate
    #         rec.black_market_rate = rec.currency_id.black_market_rate

    # @api.depends('line_ids.central_price_total', 'line_ids.black_price_total')
    # def _amount_rate_all(self):
    #     """
    #     Compute the total amounts of the SO.
    #     """
    #     for order in self:
    #         central_amount_untaxed = central_amount_tax = black_amount_untaxed = black_amount_tax = 0.0
    #         for line in order.invoice_line_ids:
    #             central_amount_untaxed += line.central_subtotal
    #             black_amount_untaxed += line.black_subtotal
    #             central_amount_tax += line.central_price_tax
    #             black_amount_tax += line.black_price_tax
    #         order.update({
    #             'central_amount_untaxed': central_amount_untaxed,
    #             'central_amount_tax': central_amount_tax,
    #             'central_amount_total': central_amount_untaxed + central_amount_tax,
    #             'black_amount_untaxed': black_amount_untaxed,
    #             'black_amount_tax': black_amount_tax,
    #             'black_amount_total': black_amount_untaxed + black_amount_tax,
    #         })

    # @api.depends('line_ids.amount_currency', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id',
    #              'second_currency_id', 'central_amount_total', 'central_amount_untaxed', 'black_amount_total',
    #              'black_amount_untaxed')
    # def _compute_rate_tax_totals_json(self):
    #     """ Computed field used for custom widget's rendering.
    #         Only set on invoices.
    #     """
    #     for move in self:
    #         if not move.is_invoice(include_receipts=True):
    #             # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
    #             move.central_tax_totals_json = None
    #             move.black_tax_totals_json = None
    #             continue
    #
    #         tax_lines_data = move._prepare_tax_lines_data_for_totals_from_invoice()
    #
    #         move.central_tax_totals_json = json.dumps({
    #             **self._get_tax_totals(move.partner_id, tax_lines_data, move.central_amount_total,
    #                                    move.central_amount_untaxed,
    #                                    move.second_currency_id),
    #             'allow_tax_edition': move.is_purchase_document(include_receipts=False) and move.state == 'draft',
    #         })
    #         move.black_tax_totals_json = json.dumps({
    #             **self._get_tax_totals(move.partner_id, tax_lines_data, move.black_amount_total,
    #                                    move.black_amount_untaxed,
    #                                    move.second_currency_id),
    #             'allow_tax_edition': move.is_purchase_document(include_receipts=False) and move.state == 'draft',
    #         })

    def _post(self, soft=True):
        for rec in self:
            if rec and rec.amount_total == 0 and not rec.payment_id and rec.move_type != 'entry':
                raise UserError(_('This invoice has a total of 0, which means there is nothing to be posted'))
            return super(AccountMove, self)._post(soft)

    # def action_reverse(self):
    #     res = super(AccountMove, self).action_reverse()
    #     if self.is_invoice():
    #         res['name'] = _('Credit Note')
    #     return res

    # def action_reverse_new(self):
    #     action = self.env["ir.actions.actions"]._for_xml_id("yoko_customization.action_view_account_move_reversal_new")
    #
    #     if self.is_invoice():
    #         # return_invoice = self.env['account.move'].search(
    #         #     [('move_type', '=', 'out_refund'), ('reversed_entry_id', '=', self.id), ('state', '!=', 'cancel'),
    #         #      ('is_reversed', '=', True)])
    #         # if return_invoice:
    #         #     raise UserError(_('A Return Invoice already exists for this invoice.'))
    #         # else:
    #         action['name'] = _('Return Invoice Creation')
    #
    #     return action

    # def button_cancel(self):
    #     res = super().button_cancel()
    #     if self.reversed_entry_id and self.is_reversed:
    #         self.is_reversed = False
    #     return res

    def button_draft(self):
        if not self.env.user.has_group("yoko_security_custom.super_user"):  ##
            logger.info(f'\n\n\n\n*****one_month_later******{self.create_date}\n\n\n\n.')
            if self.create_date:
                one_month_later = self.create_date + timedelta(days=30)
                if datetime.today() > one_month_later:
                    raise UserError(_('You cannot reset to draft because it is past one month from invoice date.'))

        for move in self:
            so_id = self.env['sale.order'].search([('name', '=like', move.invoice_origin)])  ##
            original_inv = so_id.invoice_ids.filtered(
                lambda inv: inv.reversed_entry_id.id == move.id and inv.state != 'cancel')  ##

            if move.id in so_id.invoice_ids.ids and original_inv:  ##
                raise UserError(_('You cannot reset to draft'))
        return super().button_draft()

    @api.depends('partner_id')
    def _compute_salesman_user(self):
        for move in self:
            if move.partner_id:
                move.user_salesman = move.partner_id.user_id.name
            else:
                move.user_salesman = False

    # @api.depends('partner_id', 'driver_id')
    # def _compute_collector(self):
    #     for move in self:
    #         if move.user_collector == '0':
    #             move.collector = move.driver_id
    #         elif move.user_collector == '2':
    #             move.collector = move.partner_id
    #         else:
    #             move.collector = move.partner_id.user_id.partner_id.id

    # def _action_request_return(self):
    #
    #     self.ensure_one()
    #     invoice_template = self.env.ref('yoko_customization.email_notification_invoice_return_template_id').id
    #     compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
    #
    #     group = self.env['res.groups'].search([('name', 'like', 'Indoor')], limit=1)
    #     if group:
    #         users = group.users
    #         emails = set(str(user.partner_id.id) for user in users if user.partner_id.id)
    #         ctx = dict(
    #             default_model='account.move',
    #             default_res_id=self.id,
    #             default_use_template=bool(invoice_template),
    #             default_template_id=invoice_template,
    #             default_composition_mode='comment',
    #             custom_layout='mail.mail_notification_light',
    #             force_email=True,
    #             partner_to=','.join(emails) or self.partner_ids,
    #             url=self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/web#id=' + str(
    #                 self.id) + '&model=account.move',
    #         )
    #         return {
    #             'name': _('Invoice Return Request'),
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'form',
    #             'res_model': 'mail.compose.message',
    #             'views': [(compose_form.id, 'form')],
    #             'view_id': compose_form.id,
    #             'target': 'new',
    #             'context': ctx,
    #         }
    #     else:
    #         raise ValidationError(
    #             "There is no Group called 'indoor' to send a request for, Please contact your administrator for further information")
