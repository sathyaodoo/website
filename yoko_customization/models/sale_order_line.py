from odoo import fields, models, api
import logging
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    can_edit_discount = fields.Boolean(
        string='Can Edit Discount', compute="_compute_can_edit_discount",
        required=False)

    def _compute_can_edit_discount(self):

        for record in self:
            if self.env.user.has_group('erpc_product_size.group_user_sale_discount_access') :
                record.can_edit_discount = True
            else:
                record.can_edit_discount = False

    # origin = fields.Char(string="Origin")
    # user_is_super = fields.Boolean(related='order_id.user_is_super')
    # price_and_discount_read = fields.Boolean(related='order_id.price_and_discount_read')
    price_after_discount = fields.Float(string="Initial Price", required=False, compute="_get_price_after_discount", store=True)
    # product_cost = fields.Float('Cost', related='product_id.standard_price')
    # fixed_discount = fields.Float(string="Fixed Disc.", digits="Product Price")

    # central_bank_rate = fields.Float('Central Bank rate', related='order_id.central_bank_rate')
    # central_unit_price = fields.Float('Central Unit Price', compute='_compute_currency_rate_amount', store=True)
    # central_price_tax = fields.Float(compute='_compute_central_amount', string='Central Total Tax', store=True)
    # central_price_total = fields.Monetary(compute='_compute_central_amount', string='Central Total', store=True)
    # central_subtotal = fields.Float('Central Subtotal', compute='_compute_central_amount', store=True)
    #
    # # fields for black market
    # black_market_rate = fields.Float('Black Market rate', related='order_id.black_market_rate')
    # black_unit_price = fields.Float('Black Unit Price', compute='_compute_currency_rate_amount', store=True)
    # black_price_tax = fields.Float(compute='_compute_black_amount', string='Total Tax', store=True)
    # black_price_total = fields.Monetary(compute='_compute_black_amount', string='Total', store=True)
    # black_subtotal = fields.Float('Black Subtotal', compute='_compute_black_amount', store=True)
    #
    # discount_rate_line = fields.Float('Discount Rate', related='order_id.discount_rate')
    sales_price = fields.Float(string='Sales Price', compute='_get_sales_price')
    aditional_note = fields.Text(string='Add. Note')

    @api.depends('product_id', 'product_id.list_price', 'currency_id')
    def _get_sales_price(self):
        for rec in self:
            rec.sales_price = rec.product_id.list_price * rec.currency_id.rate

    # @api.depends('central_bank_rate', 'black_market_rate', 'price_unit', 'price_subtotal')
    # def _compute_currency_rate_amount(self):
    #     for rec in self:
    #         rec.central_unit_price = rec.central_bank_rate * rec.price_unit
    #         rec.black_unit_price = rec.black_market_rate * rec.price_unit

    # @api.depends('product_uom_qty', 'discount', 'central_unit_price', 'tax_id')
    # def _compute_central_amount(self):
    #     """
    #     Compute the amounts of the SO line.
    #     """
    #     for line in self:
    #         price = line.central_unit_price * (1 - (line.discount or 0.0) / 100.0)
    #         taxes = line.tax_id.compute_all(price, line.order_id.second_currency_id, line.product_uom_qty,
    #                                         product=line.product_id, partner=line.order_id.partner_shipping_id)
    #         line.update({
    #             'central_price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'central_price_total': taxes['total_included'],
    #             'central_subtotal': taxes['total_excluded'],
    #         })
    #         if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
    #                 'account.group_account_manager'):
    #             line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    # @api.constrains('qty_delivered')
    # def check_qty_invoiced(self):
    #     if self.qty_delivered > self.product_uom_qty:
    #         raise ValidationError('cannot exceed the original quantity')
    #
    # @api.constrains('qty_invoiced')
    # def check_qty_invoiced(self):
    #     if self.qty_invoiced > self.qty_delivered:
    #         raise ValidationError('cannot exceed the original quantity')

    # @api.depends('product_uom_qty', 'discount', 'black_unit_price', 'tax_id')
    # def _compute_black_amount(self):
    #     """
    #     Compute the amounts of the SO line.
    #     """
    #     for line in self:
    #         price = line.black_unit_price * (1 - (line.discount or 0.0) / 100.0)
    #         taxes = line.tax_id.compute_all(price, line.order_id.second_currency_id, line.product_uom_qty,
    #                                         product=line.product_id, partner=line.order_id.partner_shipping_id)
    #         line.update({
    #             'black_price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'black_price_total': taxes['total_included'],
    #             'black_subtotal': taxes['total_excluded'],
    #         })
    #         if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
    #                 'account.group_account_manager'):
    #             line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    @api.depends('product_id')
    def _get_price_after_discount(self):
        for rec in self:
            if rec.product_id.show_price_after_discount == True:
                rec.price_after_discount = rec.product_id.price_after_discount
            if rec.product_id.show_price_after_discount == False:
                rec.price_after_discount = rec.product_id.list_price

    # @api.onchange('product_id')
    # def product_id_change(self):
    #     if not self.product_id:
    #         return
    #     # get the offer related to the partner and the brand
    #     partner_offer_ids = self.order_id.partner_id.sudo().offer_ids.filtered(
    #         lambda offer: offer.brand_id.id == self.product_template_id.brand_id.id)
    #
    #     if not partner_offer_ids:
    #         return
    #     offer_id = partner_offer_ids.mapped('offer_line_ids').filtered(
    #         lambda line: line.product_id.id == self.product_template_id.id)
    #
    #     if offer_id:
    #         self.discount = offer_id[0].discount  # in case there are multiple offers for the same product/partner

    # @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'discount_rate_line')
    # def _compute_amount(self):
    #     """
    #     Compute the amounts of the SO line.
    #     """
    #     for line in self:
    #         price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #         if line.discount_rate_line > 0:
    #             price -= price * (line.discount_rate_line / 100)
    #         taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
    #                                         product=line.product_id, partner=line.order_id.partner_shipping_id)
    #         line.update({
    #             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'price_total': taxes['total_included'],
    #             'price_subtotal': taxes['total_excluded'],
    #         })
    #         if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
    #                 'account.group_account_manager'):
    #             line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLineInherit, self)._prepare_invoice_line(**optional_values)
        res.update({
            # 'price_list_id': self.price_list_id.id,
            'aditional_note': self.aditional_note
        })
        return res

    def _get_display_price(self):
        # Use the default Odoo logic for display price
        return super(SaleOrderLineInherit, self)._get_display_price()

    # def _compute_qty_invoiced(self):
    #     """
    #     Re-Compute the quantity invoiced. In case of a refund (and credit note not Return Invoice),
    #     do not reduce the original one. Otherwise, leave the old computation
    #     """
    #     super(SaleOrderLineInherit, self)._compute_qty_invoiced()
    #     for line in self:
    #         invoice_lines = line._get_invoice_lines()
    #         if not any((inv_line.move_id.is_credit_note and inv_line.move_id.move_type == 'out_refund') for inv_line in
    #                    invoice_lines):
    #             continue
    #
    #         qty_invoiced = 0.0
    #         for invoice_line in invoice_lines:
    #             if invoice_line.move_id.state != 'cancel':
    #                 if invoice_line.move_id.move_type == 'out_invoice':
    #                     qty_invoiced += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
    #                                                                                   line.product_uom)
    #                 elif invoice_line.move_id.move_type == 'out_refund' and not invoice_line.move_id.is_credit_note:
    #                     qty_invoiced -= invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
    #                                                                                   line.product_uom)
    #         line.qty_invoiced = qty_invoiced

    def _prepare_procurement_values(self):
        values = super()._prepare_procurement_values()
        values['aditional_note'] = self.aditional_note
        return values

    # @api.onchange("discount")
    # def _onchange_discount(self):
    #     for line in self:
    #         if line.discount != 0:
    #             self.fixed_discount = 0.0
    #             fixed_discount = (line.price_unit * line.product_uom_qty) * (line.discount / 100.0)
    #             line.update({"fixed_discount": fixed_discount})
    #         if line.discount == 0:
    #             fixed_discount = 0.000
    #             line.update({"fixed_discount": fixed_discount})

    # @api.onchange("fixed_discount")
    # def _onchange_fixed_discount(self):
    #     for line in self:
    #         if line.fixed_discount != 0:
    #             self.discount = 0.0
    #             discount = ((self.product_uom_qty * self.price_unit) - ((self.product_uom_qty * self.price_unit) - self.fixed_discount)) / (
    #                         self.product_uom_qty * self.price_unit) * 100 or 0.0
    #             line.update({"discount": discount})
    #         if line.fixed_discount == 0:
    #             discount = 0.0
    #             line.update({"discount": discount})
