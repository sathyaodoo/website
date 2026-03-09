from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, AccessError
from odoo.exceptions import UserError

from lxml import etree

import json
import logging

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # is_price_discount = fields.Boolean(compute="_compute_is_price_discount", store=False)
    # cancel_reason = fields.Many2one('sale.lost.reason', string='Lost Reason', index=True, ondelete='restrict',
    #                                 tracking=True)
    # cancelled_date = fields.Date(string="Cancelled Date")
    # description = fields.Text(string='Description')

    # discount_rate_access = fields.Boolean(compute="_compute_access_for_discount_rate")
    # price_and_discount_read = fields.Boolean(compute="_compute_price_and_discount_read")

    # kaza_id = fields.Many2one('res.partner.kaza', related='partner_id.kaza_id', store=True)
    # city_id = fields.Many2one('res.partner.city', related='partner_id.city_id', store=True)
    state_id = fields.Many2one('res.country.state', related='partner_id.state_id', store=True)
    # customer_category_id = fields.Many2one('customer.category', related='partner_id.customer_category_id', store=True)
    parent_company_id = fields.Many2one('res.partner', string='Parent Company', related='partner_id.parent_id',
                                        domain="[('is_driver', '=', False)]")
    # driver_id = fields.Many2one('res.partner', string='Driver',
    #                             domain="[('is_driver', '=', True), ('driver_state', '=', 'active')]", tracking=True)

    total_qty = fields.Float(compute='_get_total_qty', string="Total Quantity",
                             help="Total quantities for all products")
    partner_id = fields.Many2one('res.partner', domain="[('is_driver', '=', False)]")
    # posted_invoice_existss = fields.Boolean('posted invoice exist', compute='_posted_invoice', store=True)
    # test_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)

    user_is_outdoor = fields.Boolean(compute="_compute_outdoor_check")
    user_is_indoor = fields.Boolean(compute="_compute_indoor_check")
    # user_is_super = fields.Boolean(compute="_compute_super_check")

    # invoice_date = fields.Date(string='Invoice Date', compute='_compute_invoice_date', store=True)
    # quotation_type = fields.Selection([
    #     ('rfq', 'RFQ'),
    #     ('quotation', 'Quotation')], string="Type", required=True, tracking=True, default="quotation")

    # def _compute_invoice_date(self):
    #     for order in self:
    #         min_invoice_date = None
    #         for invoice in order.invoice_ids:
    #             if not min_invoice_date or (invoice.invoice_date and invoice.invoice_date < min_invoice_date):
    #                 min_invoice_date = invoice.invoice_date
    #         order.invoice_date = min_invoice_date

    @api.depends()
    def _compute_outdoor_check(self):
        self.user_is_outdoor = self.env.user.has_group("yoko_security_custom.outdoor")

    @api.depends()
    def _compute_indoor_check(self):
        self.user_is_indoor = self.env.user.has_group("yoko_security_custom.indoor")

    # @api.depends()
    # def _compute_super_check(self):
    #     self.user_is_super = self.env.user.has_group("yoko_security_custom.super_user")

    @api.constrains('order_line')
    def _check_quantity(self):
        for rec in self.order_line:
            if rec.product_uom_qty < 0:
                raise ValidationError(_('Quantity can not be negative.'))

    def _onchange_commitment_date(self): # To add to remove warning: "The delivery date is sooner than the expected date."
        pass

    # @api.depends('posted_invoice_existss', 'state')
    # def _compute_css(self):
    #     for record in self:
    #         if record.posted_invoice_existss or record.state == 'sale':
    #             record.test_css = '<style>.o_form_button_edit {display: none !important;}.o_field_x2many_list_row_add{display: none !important;}</style>'
    #         else:
    #             record.test_css = False

    # @api.depends('invoice_ids.state')
    # def _posted_invoice(self):
    #     for rec in self:
    #         if rec.invoice_ids:
    #             invoices = rec.invoice_ids.filtered(lambda inv: inv.state in ['posted'])
    #             if invoices:
    #                 rec.posted_invoice_existss = True
    #             else:
    #                 rec.posted_invoice_existss = False
    #         else:
    #             rec.posted_invoice_existss = False

    # @api.onchange("discount_rate")
    # def _compute_access_for_discount_rate(self):
    #     self.discount_rate_access = not self.env.user.has_group("yoko_security_custom.cost_and_price")

    @api.depends("user_id")
    def _compute_price_and_discount_read(self):
        self.price_and_discount_read = not self.env.user.has_group("yoko_security_custom.discount")

    # def _onchange_commitment_date(self):
    #     pass

    # discount_rate = fields.Float('Discount Rate', digits='Account', readonly=True)
    discount_pricelists = fields.Many2many('product.pricelist')

    # @api.onchange('partner_id')
    # def _onchange_partner_id_discount_pricelist(self):
    #     pricelist = self.partner_id._origin.discount_ids.mapped('price_list_id')
    #     print("pricelist", pricelist, )
    #     if not pricelist:
    #         self.discount_pricelists = None
    #     self.discount_pricelists = pricelist

    @api.depends('order_line', 'order_line.product_uom_qty')
    def _get_total_qty(self):
        for rec in self:
            rec.total_qty = sum(rec.order_line.mapped('product_uom_qty'))

    def _get_default_second_currency_id(self):
        second_currency_id = self.env.ref('base.LBP')
        return second_currency_id if second_currency_id else None

    commitment_date = fields.Datetime('Delivery Date', copy=False, readonly=False, store=True,
                                      help="This is the delivery date promised to the customer. "
                                           "If set, the delivery order will be scheduled based on "
                                           "this date rather than product lead times.", compute="_delivery_Date")

    parent_id = fields.Many2one('res.partner', string='Parent Company', readonly=True,
                                states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                change_default=True, index=True, tracking=1,
                                domain="[('is_driver', '=', False), ('type', '!=', 'private'), ('company_id', 'in', (False, company_id))]")

    @api.constrains('commitment_date')
    def _check_date(self):
        if self.env.context.get('force_update'):
            """If yes, this means it 's updated through server action"""
            return
        now = fields.Datetime.now()
        for record in self:
            if record.commitment_date and record.commitment_date < now:
                raise ValidationError("Date cannot be set in the past.")
     
    @api.onchange('parent_id')
    def onchange_parent_id(self):
        if self.parent_id != self.partner_id.parent_id:  # In case the parent is not the parent of the current partner
            self.partner_id = False
        if self.parent_id:
            domain = [('parent_id', '=', self.parent_id.id), ('is_driver', '=', False)]
        else:
            domain = [('is_driver', '=', False)]
        return {'domain': {'partner_id': domain}}

    @api.onchange('partner_id')
    def partner_id_onchange(self):
        if self.partner_id:
            self.parent_id = self.partner_id.parent_id

    # @api.onchange('quotation_type')
    # def onchange_quotation_type(self):
    #     if self.quotation_type == 'rfq':
    #         self.delivery_term = '-1'

    def _default_delivery_term(self):
        return '-1'

    delivery_term = fields.Selection([
        ('-1', 'No Delivery'),
        ('0', 'Immediate'),
        ('1', 'Today'),
        ('2', 'Tomorrow'),
        ('3', 'Later')], string="Delivery Term", required=True, default=_default_delivery_term)

    @api.depends('delivery_term')
    def _delivery_Date(self):
        for rec in self:
            if rec.delivery_term == '0':
                rec.commitment_date = datetime.now()
            elif rec.delivery_term == '1':
                rec.commitment_date = datetime.now()
            elif rec.delivery_term == '2':
                rec.commitment_date = datetime.now() + timedelta(days=1)
            else:
                rec.commitment_date = None

    def update_delivery_date(self):
        """This will be used in action to update dates for old data"""
        for rec in self:
            rec.commitment_date = rec.create_date

    second_currency_id = fields.Many2one('res.currency', string='Second Currency', required=True, readonly=False,
                                         store=True,
                                         default=_get_default_second_currency_id)

    # # fields for Central Bank (central_name_of_field )  that you need to add fields in this area
    # central_bank_rate = fields.Float('Central Bank rate', copy=False)
    # central_amount_untaxed = fields.Monetary(string='Central Untaxed Amount', store=True, compute='_amount_rate_all',
    #                                          tracking=5)
    # central_amount_tax = fields.Monetary(string='Central Taxes', store=True, compute='_amount_rate_all')
    # central_amount_total = fields.Monetary(string='Central Total', store=True, compute='_amount_rate_all', tracking=4)
    # central_tax_totals_json = fields.Char(compute='_compute_central_tax_totals_json')
    #
    # # fields for Central Bank (black_name_of_field )  that you need to add fields in this area
    # black_market_rate = fields.Float('Black Market rate', copy=False)
    # black_amount_untaxed = fields.Monetary(string='Black Untaxed Amount', store=True, compute='_amount_rate_all',
    #                                        tracking=5)
    # black_amount_tax = fields.Monetary(string='Black Taxes', store=True, compute='_amount_rate_all')
    # black_amount_total = fields.Monetary(string='Black Total', store=True, compute='_amount_rate_all', tracking=4)
    # black_tax_totals_json = fields.Char(compute='_compute_black_tax_totals_json')
    #
    # rate_access = fields.Boolean(compute="_compute_access_for_rate")

    # @api.onchange("rate_access")
    # def _compute_access_for_rate(self):
    #     # instead of wrtiting a long conition like "user.has_group(blabla) or user.has(blabla)  or user.has(blabla)",  i thoght of this : determine if True in list
    #     accessabilty_list = [self.env.user.has_group("sales_team.group_sale_manager"),
    #                          self.env.user.has_group("base.group_erp_manager"),
    #                          self.env.user.has_group("base.group_system")]
    #     print("accessabilty_list")
    #     print(accessabilty_list)
    #     self.rate_access = True in accessabilty_list and not self.env.user.has_group(
    #         "yoko_currency_rate.cost_and_price")

    def _get_BMR_rate(self):
        current_rate = self.env.ref('base.LBP')
        return current_rate.rate

    current_rate = fields.Float("LBP Rate", default=_get_BMR_rate)

    untaxed_custom_amount = fields.Monetary(currency_field='second_currency_id', tracking=5, store=True,
                                            compute="_compute_tax_and_untaxed", string="Untaxed LBP Amount")
    taxed_custom_amount = fields.Monetary(currency_field='second_currency_id', store=True,
                                          compute="_compute_tax_and_untaxed", string="VAT LBP")
    in_lbp_currency = fields.Boolean(compute="_detect_order_in_lbp_currency")

    total_vat = fields.Monetary(currency_field='currency_id', store=True,
                                compute="_compute_amount_total_with_fixed_tax", string="VAT")
    amount_total_ttc = fields.Monetary(currency_field='currency_id', store=True,
                                       compute="_compute_amount_total_with_fixed_tax", string="Total TTC")
    total_vat_lbp = fields.Monetary(currency_field='second_currency_id', compute="_compute_total_vat_lbp",
                                    string="VAT LBP")

    @api.depends('currency_id', 'second_currency_id', 'amount_total')
    def _compute_amount_total_with_fixed_tax(self):
        for rec in self:
            rec.total_vat = rec.amount_total * 0.11
            rec.amount_total_ttc = rec.amount_total + rec.total_vat

    @api.depends('total_vat', 'currency_id', 'second_currency_id')
    def _compute_total_vat_lbp(self):
        for rec in self:
            if rec.currency_id.name in ['LBP', 'BMR']:
                rec.total_vat_lbp = rec.total_vat
            else:  # Convert it first to primary currency(e.g USD)
                rec.total_vat_lbp = rec.total_vat * rec.currency_id.rate * rec.second_currency_id.inverse_rate

    @api.onchange("currency_id")
    def _detect_order_in_lbp_currency(self):
        lbp_curr = self.env['res.currency'].search([('name', 'in', ['LBP', 'BMR'])])
        if self.currency_id.id in lbp_curr.ids:
            self.in_lbp_currency = True
        else:
            self.in_lbp_currency = False

    @api.depends('order_line.price_unit', 'order_line.product_uom_qty', 'current_rate', 'currency_id', 'amount_untaxed')
    def _compute_tax_and_untaxed(self):
        for rec in self:
            black_market_currency = self.env['res.currency'].search([('name', '=', 'BMR')])
            logger.info(rec.amount_untaxed)
            # untaxed_custom = rec.amount_untaxed * rec.black_market_currency.rate

            untaxed_custom = rec.amount_untaxed * rec.current_rate
            # To include EURO rate within the amount
            if rec.currency_id.name == "EUR":
                untaxed_custom = untaxed_custom * rec.currency_id.inverse_rate

            logger.info(rec.amount_tax)

            # In case of LBP, BMR Don not apply Conversion Rate, it is already applied
            if rec.currency_id.name in ['LBP', 'BMR']:
                taxed_custom_amount = rec.amount_tax
            else:  # Convert it first to primary currency(e.g USD)
                taxed_custom_amount = rec.amount_tax * rec.currency_id.inverse_rate * rec.second_currency_id.rate

            logger.info(rec.second_currency_id.rate)
            logger.info(taxed_custom_amount)
            rec.update({
                'untaxed_custom_amount': untaxed_custom,
                'taxed_custom_amount': taxed_custom_amount
            })

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        logger.info("Pre")
        black_market_currency = self.env['res.currency'].search([('name', '=', 'BMR')])
        if black_market_currency:
            res.update({
                # 'warehouse_id': self.warehouse_id.id,
                'current_rate': black_market_currency.rate,
                # 'from_order': True,
            })
        res['parent_company_id'] = self.parent_id.id
        res['delivery_date'] = self.commitment_date
        # res['delivery_term'] = self.delivery_term
        return res

    # using the main function
    # @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    # def _compute_tax_totals_json(self):
    #
    #     def compute_taxes(order_line):
    #         price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
    #         if self.discount_rate > 0:
    #             price -= price * (self.discount_rate / 100)
    #         order = order_line.order_id
    #         return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
    #                                                      product=order_line.product_id,
    #                                                      partner=order.partner_shipping_id)
    #
    #     account_move = self.env['account.move']
    #     for order in self:
    #         tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line,
    #                                                                                      compute_taxes)
    #         logger.info("main tax_lines_data")
    #         logger.info(tax_lines_data)
    #         tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
    #                                                   order.amount_untaxed, order.currency_id)
    #
    #         order.tax_totals_json = json.dumps(tax_totals)

    # @api.onchange('currency_id')
    # def onchange_currency_id_rate(self):
    #     for rec in self:
    #         rec.central_bank_rate = rec.currency_id.central_bank_rate
    #         rec.black_market_rate = rec.currency_id.black_market_rate

    # @api.depends('order_line.central_price_total', 'order_line.black_price_total')
    # def _amount_rate_all(self):
    #     """
    #     Compute the total amounts of the SO.
    #     """
    #     for order in self:
    #         central_amount_untaxed = central_amount_tax = black_amount_untaxed = black_amount_tax = 0.0
    #         for line in order.order_line:
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

    # @api.depends('order_line.tax_id', 'order_line.central_unit_price', 'central_amount_total', 'central_amount_untaxed')
    # def _compute_central_tax_totals_json(self):
    #     def compute_taxes(order_line):
    #         price = order_line.central_unit_price * (1 - (order_line.discount or 0.0) / 100.0)
    #         order = order_line.order_id
    #         return order_line.tax_id._origin.compute_all(price, self.second_currency_id, order_line.product_uom_qty,
    #                                                      product=order_line.product_id,
    #                                                      partner=order.partner_shipping_id)
    #
    #     account_move = self.env['account.move']
    #     for order in self:
    #         tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line,
    #                                                                                      compute_taxes)
    #         tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.central_amount_total,
    #                                                   order.central_amount_untaxed, order.second_currency_id)
    #         order.central_tax_totals_json = json.dumps(tax_totals)

    # @api.depends('order_line.tax_id', 'order_line.black_unit_price', 'black_amount_total', 'black_amount_untaxed')
    # def _compute_black_tax_totals_json(self):
    #     def compute_taxes(order_line):
    #         price = order_line.black_unit_price * (1 - (order_line.discount or 0.0) / 100.0)
    #         order = order_line.order_id
    #         return order_line.tax_id._origin.compute_all(price, self.second_currency_id, order_line.product_uom_qty,
    #                                                      product=order_line.product_id,
    #                                                      partner=order.partner_shipping_id)
    #
    #     account_move = self.env['account.move']
    #     for order in self:
    #         tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line,
    #                                                                                      compute_taxes)
    #         tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.black_amount_total,
    #                                                   order.black_amount_untaxed, order.second_currency_id)
    #         order.black_tax_totals_json = json.dumps(tax_totals)

    @api.constrains('state')
    def sales_order_validation_state(self):
        if self.state not in ['draft', 'cancel']:
            invoices = self.invoice_ids.filtered(
                lambda inv: inv.state not in ['posted', 'cancel'] and inv.amount_total == 0)
            if self and invoices:
                raise ValidationError('Draft Invoices have an amount of 0 please adjust to continue')
            if self and self.amount_total == 0 and not self.is_promo:
                raise ValidationError('Sales order has an amount of 0, please adjust to continue')

    # def action_confirm(self):
    #     if self.quotation_type == 'rfq':
    #         raise ValidationError("You can't confirm an Order with type 'RFQ'!")
    #     super(SaleOrder, self).action_confirm()

    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent'])
        return orders.write({
            'state': 'draft',
            'signature': False,
            'signed_by': False,
            # 'signed_on': False,
            # 'cancel_reason': False,
            # 'cancelled_date': False,
            # 'description': False,
        })

    # def _action_request_cancellation(self):
    #
    #     self.ensure_one()
    #     saleorder_template = self.env.ref('yoko_customization.email_notification_cancel_so_template_id').id
    #     compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
    #
    #     group = self.env['res.groups'].search([('name', 'like', 'Indoor')], limit=1)
    #     if group:
    #         users = group.users
    #         emails = set(str(user.partner_id.id) for user in users if user.partner_id.id)
    #         ctx = dict(
    #             default_model='sale.order',
    #             default_res_id=self.id,
    #             default_use_template=bool(saleorder_template),
    #             default_template_id=saleorder_template,
    #             default_composition_mode='comment',
    #             custom_layout='mail.mail_notification_light',
    #             force_email=True,
    #             partner_to=','.join(emails) or self.partner_ids,
    #             url=self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/web#id=' + str(
    #                 self.id) + '&model=sale.order',
    #         )
    #         return {
    #             'name': _('Cancellation Request Email'),
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

    # def _action_request_confirmation(self):
    #
    #     self.ensure_one()
    #
    #     saleorder_template = self.env.ref('yoko_customization.email_notification_confirm_so_template_id').id
    #     compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
    #     group_id = self.env.ref('yoko_security_custom.indoor').id
    #
    #     group = self.env['res.groups'].search([('id', '=', group_id)])
    #     if group:
    #         users = group.users
    #
    #         emails = set(str(user.partner_id.id) for user in users if user.partner_id.id)
    #         ctx = dict(
    #             default_model='sale.order',
    #             default_res_id=self.id,
    #             default_use_template=bool(saleorder_template),
    #             default_template_id=saleorder_template,
    #             default_composition_mode='comment',
    #             custom_layout='mail.mail_notification_light',
    #             force_email=True,
    #             partner_to=','.join(emails) or self.partner_ids,
    #             url=self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/web#id=' + str(
    #                 self.id) + '&model=sale.order',
    #             is_confirmation_request=True,
    #         )
    #         return {
    #             'name': _('Confirmation Request Email'),
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

    # def action_cancel(self):
    #
    #     is_super_user = self.env.user.has_group("yoko_security_custom.super_user")
    #
    #     if not is_super_user and self.state not in ['draft', 'cancel']:
    #         for rec in self.order_line:
    #             if rec.qty_delivered != 0:
    #                 raise ValidationError(
    #                     _('This sales order cannot be cancelled, please do a return for them to continue'))
    #
    #         for rec in self.order_line:
    #             if rec.qty_invoiced != 0:
    #                 raise ValidationError(
    #                     _('This sales order cannot be cancelled please check the invoices and cancel them to proceed'))
    #
    #     return {
    #         'name': _('Cancel Sales Order'),
    #         'view_mode': 'form',
    #         'res_model': 'sale.order.cancel',
    #         'view_id': self.env.ref('yoko_customization.sale_order_cancel_view_reasons').id,
    #         'type': 'ir.actions.act_window',
    #         'context': {'default_order_id': self.id},
    #         'target': 'new'
    #     }

    # TODO GR: to do it later it affects in payment
    # def action_confirm(self):
    #     user = self.env.user
    #     logger.info(f'\n\n\n *****{user.name}')
    #     if not user.has_group('yoko_customization.confirm_so'):
    #         logger.info(f'\n\n\n *****{self.id}')
    #         raise ValidationError(
    #             _("You do not have the permission to confirm sale orders."))
    #
    #     return super(SaleOrder, self).action_confirm()


class InheritStockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_term = fields.Selection(related='sale_id.delivery_term', store=True)
    picking_type_code = fields.Selection(related='picking_type_id.code', store=True)
