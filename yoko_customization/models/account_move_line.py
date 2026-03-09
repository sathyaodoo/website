# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    sales_price = fields.Float(string='Sales Price', compute='_get_sales_price', store=True)

    @api.depends('product_id', 'product_id.list_price', 'currency_id')
    def _get_sales_price(self):
        for rec in self:
            rec.sales_price = rec.product_id.list_price * rec.currency_id.rate

    # user_is_super = fields.Boolean(related='move_id.user_is_super')
    # price_and_discount_read = fields.Boolean(related='move_id.price_and_discount_read')
    # Disregarded for sale_invoice_fixed_discount model
    # fixed_discount = fields.Float(string="Fixed Disc.", digits="Product Price", default=0.000)

    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0, readonly=False)

    price_after_discount = fields.Float(string="Initial Price", required=False, compute="_compute_price_after_discount",
                                        store=True)

    @api.depends('sale_line_ids')
    def _compute_price_after_discount(self):
        for line in self:
            if line.sale_line_ids:
                line.price_after_discount = line.sale_line_ids[0].price_after_discount
            else:
                line.price_after_discount = line.product_id.lst_price

    # central_bank_rate = fields.Float('Central Bank rate', related='move_id.central_bank_rate')
    # central_unit_price = fields.Float('Central Unit Price', compute='_compute_currency_rate_amount', store=True)
    # central_price_tax = fields.Float(compute='_compute_central_amount', string='Central Total Tax', store=True)
    # central_price_total = fields.Monetary(compute='_compute_central_amount', string='Central Total', store=True)
    # central_subtotal = fields.Float('Central Subtotal', compute='_compute_central_amount', store=True)
    #
    # # fields for black market
    # black_market_rate = fields.Float('Black Market rate', related='move_id.black_market_rate')
    # black_unit_price = fields.Float('Black Unit Price', compute='_compute_currency_rate_amount', store=True)
    # black_price_tax = fields.Float(compute='_compute_black_amount', string='Total Tax', store=True)
    # black_price_total = fields.Monetary(compute='_compute_black_amount', string='Total', store=True)
    # black_subtotal = fields.Float('Black Subtotal', compute='_compute_black_amount', store=True)
    aditional_note = fields.Text(
        string="Add. Note",
        related='sale_line_ids.aditional_note',
        store=True,
        readonly=True,
    )
    product_cost = fields.Float('Cost', related='product_id.standard_price', store=True)
    # discount_rate_line = fields.Float('Discount Rate', readonly=False)
    # is_sales = fields.Boolean(
    #     string='Is_sales',
    #     required=False)

    # price_list_id = fields.Many2one('product.pricelist', compute='product_change_price_list', store=True,
    #                                 readonly=False, string="Client Discount")
    price_list_id = fields.Many2one('product.pricelist', store=True,
                                    readonly=False, string="Client Discount")
    final_price = fields.Float(compute="_compute_final_price")
    # deduction_price = fields.Monetary(string="Deduction", default=0)
    # warehouse_id = fields.Many2one('stock.warehouse', compute='_compute_warehouse', store=True, string="Warehouse")

    # @api.depends('sale_line_ids', 'sale_line_ids.warehouse_id')
    # def _compute_warehouse(self):
    #     for line in self:
    #         sale_line_ids = line.sale_line_ids
    #         if sale_line_ids:
    #             line.warehouse_id = sale_line_ids.warehouse_id.id
    #         else:
    #             line.warehouse_id = None

    # @api.onchange('deduction_price')
    # def onchange_deduct_price(self):
    #     """To call the onchange function to include Deduction Price"""
    #     if not self:
    #         return
    #     for line in self:
    #         line._compute_totals()

    @api.onchange('discount', 'price_unit')
    def _compute_final_price(self):
        for rec in self:
            rec.final_price = (1 - (rec.discount / 100)) * rec.price_unit

    # @api.depends('product_id', 'move_id.discount_pricelists', 'move_id')
    # def product_change_price_list(self):
    #     for rec in self:
    #         price_list = rec.move_id.discount_pricelists._origin.filtered(
    #             lambda r: r.brand_id == rec.product_id.brand_id)
    #         if price_list:
    #             rec.price_list_id = price_list[0].id
    #         else:
    #             rec.price_list_id = None

    # @api.depends('quantity', 'discount', 'black_unit_price', 'tax_ids')
    # def _compute_black_amount(self):
    #     """
    #     Compute the amounts of the SO line.
    #     """
    #     taxes = {}
    #     for line in self:
    #         price = line.black_unit_price * (1 - (line.discount or 0.0) / 100.0)
    #         taxes = line.tax_ids.compute_all(price, line.move_id.second_currency_id, line.quantity,
    #                                          product=line.product_id, partner=line.move_id.partner_shipping_id)
    #         line.update({
    #             'black_price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'black_price_total': taxes['total_included'],
    #             'black_subtotal': taxes['total_excluded'],
    #         })
    #         # if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
    #         #         'account.group_account_manager'):
    #         #     line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    # @api.depends('quantity', 'discount', 'central_unit_price', 'tax_ids')
    # def _compute_central_amount(self):
    #     """
    #     Compute the amounts of the SO line.
    #     """
    #     for line in self:
    #         price = line.central_unit_price * (1 - (line.discount or 0.0) / 100.0)
    #         taxes = line.tax_ids.compute_all(price, line.move_id.second_currency_id, line.quantity,
    #                                          product=line.product_id, partner=line.move_id.partner_shipping_id)
    #         line.update({
    #             'central_price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'central_price_total': taxes['total_included'],
    #             'central_subtotal': taxes['total_excluded'],
    #         })
    #         if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
    #                 'account.group_account_manager'):
    #             line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    # @api.depends('central_bank_rate', 'black_market_rate', 'price_unit', 'price_subtotal')
    # def _compute_currency_rate_amount(self):
    #     for rec in self:
    #         rec.central_unit_price = rec.central_bank_rate * rec.price_unit
    #         rec.black_unit_price = rec.black_market_rate * rec.price_unit

    # @api.constrains('quantity')
    # def _check_quantity(self):
    #     for rec in self:
    #         if not rec.product_id.type in ['consu', 'service']:
    #             if not rec.move_id.reversed_entry_id:
    #                 if rec and rec.sale_line_ids:
    #                     sale_line = rec.sale_line_ids[0]
    #                     if rec.quantity > sale_line.qty_delivered:
    #                         sale_order = self.env['sale.order'].search([('name', '=', rec.move_id.invoice_origin)])
    #                         picking_ids = sale_order.picking_ids.filtered(
    #                             lambda pick: pick.state in ['confirmed', 'done'] and 'Return of' in pick.origin)
    #                         if sale_order and picking_ids:
    #                             for transfer in picking_ids:
    #                                 if transfer.picking_type_id.name == 'Returns':
    #                                     line = transfer.move_ids_without_package[0]
    #                                     if (line.quantity_done - rec.quantity == 0) and (
    #                                             line.product_id == rec.product_id):
    #                                         continue
    #                                     else:
    #                                         raise ValidationError(
    #                                             "Quantity exceeds the Sales Order delivered Quantity")
    #                                 else:
    #                                     raise ValidationError(
    #                                         "Quantity exceeds the Sales Order delivered Quantity")
    #                         else:
    #                             raise ValidationError(
    #                                 "Quantity exceeds the Sales Order delivered Quantity")

    # @api.model_create_multi
    # def create(self, vals_list):
    #     discount_rate = False
    #     is_sale = False
    #     result = super(AccountMoveLineInherit, self).create(vals_list)
    #
    #     # for rec in result:
    #     #     if rec.product_id.show_price_after_discount == True:
    #     #         rec.price_after_discount = rec.product_id.price_after_discount
    #     #     if rec.product_id.show_price_after_discount == False:
    #     #         rec.price_after_discount = rec.product_id.list_price
    #
    #     if not result.sale_line_ids and result:
    #         no_product_lines = result[0].move_id.invoice_line_ids.filtered(lambda l: not l.product_id)
    #         # if no_product_lines and result[0].move_id.move_type == "out_invoice":
    #         #     raise ValidationError('Invoice has one or more lines without a product')
    #
    #     for vals in vals_list:
    #         if vals.get('discount_rate_line'):
    #             discount_rate = True
    #     if discount_rate:
    #         rec = super(AccountMoveLineInherit, self).with_context(discount_rate=discount_rate).create(vals_list)
    #         for line in rec:
    #             line._compute_totals()
    #         return rec
    #     return result

    # def write(self, vals):
    #     result = super(AccountMoveLineInherit, self).write(vals)
    #     for rec in self:
    #         if 'product_id' in vals:
    #             # product_id = vals.get('product_id')
    #             product_id = self.env['product.template'].search([('id', '=', vals.get('product_id'))])
    #             if product_id.show_price_after_discount == True:
    #                 rec.price_after_discount = rec.product_id.price_after_discount
    #     return result

    # @api.model
    # def _get_fields_onchange_balance_model(self, quantity, discount, amount_currency, move_type, currency, taxes,
    #                                        price_subtotal, force_computation=False):
    #     vals = {}
    #     if not self.env.context.get('discount_rate'):
    #         vals = super(AccountMoveLineInherit, self)._get_fields_onchange_balance_model(
    #             quantity,
    #             discount,
    #             amount_currency,
    #             move_type,
    #             currency,
    #             taxes,
    #             price_subtotal,
    #             force_computation=force_computation
    #         )
    #     return vals

    # @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids', 'discount_rate_line')
    # def _onchange_price_subtotal(self):
    #     super(AccountMoveLineInherit, self)._onchange_price_subtotal()

    # @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id', 'discount_rate_line')
    # def _compute_totals(self):
    #     super(AccountMoveLineInherit, self)._compute_totals()

    # @api.model
    # def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes,
    #                                         move_type):
    #     ''' This method is used to compute 'price_total' & 'price_subtotal'.
    #
    #     :param price_unit:  The current price unit.
    #     :param quantity:    The current quantity.
    #     :param discount:    The current discount.
    #     :param currency:    The line's currency.
    #     :param product:     The line's product.
    #     :param partner:     The line's partner.
    #     :param taxes:       The applied taxes.
    #     :param move_type:   The type of the move.
    #     :return:            A dictionary containing 'price_subtotal' & 'price_total'.
    #     '''
    #     res = {}
    #
    #     line_discount_price_unit = price_unit * (1 - (discount / 100.0))
    #
    #     subtotal = quantity * line_discount_price_unit
    #     subtotal -= subtotal * (self.discount_rate_line / 100)
    #
    #     # Compute 'price_total'.
    #     if taxes:
    #         if self.discount_rate_line != 0:
    #             line_discount_price_unit -= line_discount_price_unit * (self.discount_rate_line / 100)
    #         taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
    #                                                                          quantity=quantity, currency=currency,
    #                                                                          product=product, partner=partner,
    #                                                                          is_refund=move_type in (
    #                                                                              'out_refund', 'in_refund'))
    #         res['price_subtotal'] = taxes_res['total_excluded']
    #         res['price_total'] = taxes_res['total_included']
    #     else:
    #         res['price_total'] = res['price_subtotal'] = subtotal
    #     # In case of multi currency, round before it's use for computing debit credit
    #     if currency:
    #         res = {k: currency.round(v) for k, v in res.items()}
    #     return res
    #
    # def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None,
    #                                   partner=None, taxes=None, move_type=None):
    #     if self.move_id.is_credit_note and self.deduction_price > 0:  # In case it is credit note, just change the price unit
    #         price_unit = self.price_unit - self.deduction_price
    #     res = super(AccountMoveLineInherit, self)._get_price_total_and_subtotal(price_unit, quantity, discount,
    #                                                                             currency,
    #                                                                             product, partner, taxes, move_type)
    #
    #     return res

# Disregarded for sale_invoice_fixed_discount model
# @api.onchange("discount")
# def _onchange_discount(self):
#     for line in self:
#         if line.discount != 0:
#             self.fixed_discount = 0.0
#             fixed_discount = (line.price_unit * line.quantity) * (line.discount / 100.0)
#             line.update({"fixed_discount": fixed_discount})
#         if line.discount == 0:
#             fixed_discount = 0.000
#             line.update({"fixed_discount": fixed_discount})

# @api.onchange("fixed_discount")
# def _onchange_fixed_discount(self):
#     for line in self:
#         if line.fixed_discount != 0:
#             self.discount = 0.0
#             discount = ((self.quantity * self.price_unit) - (
#                         (self.quantity * self.price_unit) - self.fixed_discount)) / (
#                                self.quantity * self.price_unit) * 100 or 0.0
#             line.update({"discount": discount})
#         if line.fixed_discount == 0:
#             discount = 0.0
#             line.update({"discount": discount})
