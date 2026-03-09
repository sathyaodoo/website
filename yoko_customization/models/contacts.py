# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError, UserError, AccessError

_logger = logging.getLogger(__name__)

DOMAIN_SEARCH = {
    ("=", False): ("=", 0),
    ("=", True): (">=", 1),
    ("!=", False): (">=", 1),
    ("!=", True): ("=", 0),
}


class ResPartnerInh(models.Model):
    _inherit = 'res.partner'

    # is_customer = fields.Boolean(
    #     compute="_compute_is_customer",
    #     # inverse="_inverse_is_customer",
    #     search="_search_is_customer",
    #     string="Is a Customer",
    # )
    #
    # is_supplier = fields.Boolean(
    #     compute="_compute_is_supplier",
    #     # inverse="_inverse_is_supplier",
    #     search="_search_is_supplier",
    #     string="Is a Supplier",
    # )
    driver_id = fields.Many2one('res.partner', string="Driver", required=False,
                                domain="[('is_driver', '=', True), ('driver_state', '=', 'active')]", tracking=True)
    # collection_type = fields.Selection(
    #     [("0", "Driver"), ("1", "Salesman"), ("2", "Customer")], string="Collection Type", required=False,
    #     tracking=True)

    # offer_ids = fields.Many2many('product.offer', string='Offers')
    # comma_separated_field = fields.Char('Offers', compute='_onchange_offer_field')

    # @api.depends('offer_ids')
    # def _onchange_offer_field(self):
    #     self.comma_separated_field = ','.join(self.offer_ids.mapped('name')) if self.offer_ids else False

    birthdate = fields.Date(string="Birth Date")
    # is_company = fields.Boolean("is Company")
    # is_driver = fields.Boolean("is Driver", default=False)
    # code = fields.Char(string="Code")
    # description = fields.Text(string='Description')
    driver_state = fields.Selection(string='Driver State', selection=[('active', 'Active'), ('inactive', 'In-Active')],
                                    default="active")

    # invoice_currency_id = fields.Many2one('res.currency', string="Invoicing Currency")
    # disable_invoice = fields.Boolean("Can't Be Invoiced")
    # blocked = fields.Boolean("Blocked")

    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     if args is None:
    #         args = []
    #
    #     args += [('blocked', '=', False)]
    #
    #     return super(ResPartnerInh, self).name_search(name, args, operator, limit)

    # customer_category_idsss = fields.Many2many('customer.category', string="Customer Category",
    #                                            compute="_compute_customer_category_idsss")

    # def _compute_customer_category_idsss(self):
    #     for partner in self:
    #         domain = []
    #         if partner.is_customer and not partner.is_supplier:
    #             domain = [('type', '=', 'customer')]
    #         elif partner.is_supplier and not partner.is_customer:
    #             domain = [('type', '=', 'supplier')]
    #
    #         # Search for the customer category based on the domain
    #         customer_category = self.env['customer.category'].search(domain)
    #
    #         # Assign the customer_category.id to the field
    #         partner.customer_category_idsss = customer_category.ids

    # def _default_customer_category_id(self):
    #     if self._context.get('is_customer_category_crm', False):
    #         default_category = self.env['customer.category'].search([('name', '=', 'ERP')])
    #         return default_category.id if default_category else False
    #     return False

    # customer_category_id = fields.Many2one('customer.category', string="Customer Category", required=False,
    #                                        default=_default_customer_category_id)
    #
    # business_id = fields.Many2one('business.type', string="Type of Business", required=False)
    # customer_class_id = fields.Many2one('yoko.class', string='Class')
    second_phone = fields.Char("Phone 2")
    # third_phone = fields.Char("Phone 3")
    # credit_limit = fields.Float("Credit Limit")
    # target = fields.Float("Target")
    # extension = fields.Char(string='Extension', required=False)
    # odoo fields
    state_id = fields.Many2one("res.country.state", string='Region', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    # zip = fields.Char(change_default=True, string='Kazaa')
    # kaza_id = fields.Many2one('res.partner.kaza', string="Kaza LEB",
    #                           domain="['&', ('state_id','=',state_id), ('state_id', '!=', False)]", required=True)
    # city_id = fields.Many2one('res.partner.city', string="Reg City",
    #                           domain="['&', ('kaza_id','=',kaza_id), ('kaza_id', '!=', False)]", required=True)
    # discount_ids = fields.One2many(comodel_name='res.partner.discount', inverse_name='partner_id', string='Discounts',
    #                                required=False)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if self._context.get('is_driver'):
    #             vals['is_driver'] = True
    #         if self._context.get('is_customer_category_crm', False):
    #             vals['customer_category_id'] = self.env['customer.category'].search([('name', '=', 'ERP')], limit=1).id
    #     return super(ResPartnerInh, self).create(vals_list)
    #
    def _get_lebnan_country(self):
        country_id = self.env['res.country'].search([('code', '=', 'LB')])
        return country_id if country_id else None

    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_get_lebnan_country)

    @api.onchange('parent_id')
    def _parent_id_autofill(self):
        if self and self.parent_id:
            self.phone = self.parent_id.phone
            self.email = self.parent_id.email
            self.website = self.parent_id.website
            self.second_phone = self.parent_id.second_phone
            self.category_id = self.parent_id.category_id
            self.property_account_receivable_id = self.parent_id.property_account_receivable_id
            self.property_account_payable_id = self.parent_id.property_account_payable_id
            self.property_payment_term_id = self.parent_id.property_payment_term_id
            self.property_supplier_payment_term_id = self.parent_id.property_supplier_payment_term_id
            self.property_product_pricelist = self.parent_id.property_product_pricelist
            self.user_id = self.parent_id.user_id

    # @api.depends("customer_rank")
    # def _compute_is_customer(self):
    #     for partner in self:
    #         partner.is_customer = bool(partner.customer_rank)

    # @api.depends("supplier_rank")
    # def _compute_is_supplier(self):
    #     for partner in self:
    #         partner.is_supplier = bool(partner.supplier_rank)
    #
    # def _inverse_is_customer(self):
    #     self.filtered(lambda p: not p.is_customer).write({"customer_rank": 0})
    #     self.filtered(lambda p: p.is_customer and not p.customer_rank).write(
    #         {"customer_rank": 1}
    #     )
    #
    # def _search_is_customer(self, operator, value):
    #     if operator not in ["=", "!="] or not isinstance(value, bool):
    #         raise UserError(_("Operation not supported"))
    #     operator, value = DOMAIN_SEARCH.get((operator, value))
    #     return [("customer_rank", operator, value)]

    # def _inverse_is_supplier(self):
    #     self.filtered(lambda p: not p.is_supplier).write({"supplier_rank": 0})
    #     self.filtered(lambda p: p.is_supplier and not p.supplier_rank).write(
    #         {"supplier_rank": 1}
    #     )
    #
    # def _search_is_supplier(self, operator, value):
    #     if operator not in ["=", "!="] or not isinstance(value, bool):
    #         raise UserError(_("Operation not supported"))
    #     operator, value = DOMAIN_SEARCH.get((operator, value))
    #     return [("supplier_rank", operator, value)]

    # @api.onchange('parent_id')
    # def _onchange_parent_id(self):
    #     if self.parent_id:
    #         self.customer_category_id = self.parent_id.customer_category_id
    #         self.business_id = self.parent_id.business_id
    #         self.invoice_currency_id = self.parent_id.invoice_currency_id
    #         self.category_id = self.parent_id.category_id
    #         self.customer_class_id = self.parent_id.customer_class_id
    #         self.property_payment_term_id = self.parent_id.property_payment_term_id
    #         self.property_supplier_payment_term_id = self.parent_id.property_supplier_payment_term_id
    #         self.credit_limit = self.parent_id.credit_limit
    #         self.target = self.parent_id.target
    #         self.property_product_pricelist = self.parent_id.property_product_pricelist
    #         self.user_id = self.parent_id.user_id

    def write(self, vals):
        res = super(ResPartnerInh, self).write(vals)

        if self.child_ids:
            for rec in self.child_ids:
                # if vals.get('customer_category_id'):
                #     rec.customer_category_id = vals.get('customer_category_id')
                # if vals.get('business_id'):
                #     rec.business_id = vals.get('business_id')
                # if vals.get('customer_class_id'):
                #     rec.customer_class_id = vals.get('customer_class_id')
                if vals.get('property_payment_term_id'):
                    rec.property_payment_term_id = vals.get('property_payment_term_id')
                if vals.get('property_supplier_payment_term_id'):
                    rec.property_supplier_payment_term_id = vals.get('property_supplier_payment_term_id')
                # if vals.get('credit_limit'):
                #     rec.credit_limit = vals.get('credit_limit')
                # if vals.get('target'):
                #     rec.target = vals.get('target')
                if vals.get('property_product_pricelist'):
                    rec.property_product_pricelist = vals.get('property_product_pricelist')
                if vals.get('user_id'):
                    rec.user_id = vals.get('user_id')
                # if vals.get('is_customer'):
                #     rec.is_customer = vals.get('is_customer')
                # if vals.get('is_supplier'):
                #     rec.is_supplier = vals.get('is_supplier')
                # if vals.get('offer_ids'):
                #     rec.offer_ids = vals.get('offer_ids')
                # if vals.get('collection_type'):
                #     rec.collection_type = vals.get('collection_type')

        return res

    # @api.constrains('customer_category_id')
    # def _accounting_accounts(self):
    #     if self.customer_category_id:
    #         if self.customer_category_id.account_receivable_id.id and self.customer_category_id.account_payable_id.id:
    #             self.property_account_receivable_id = self.customer_category_id.account_receivable_id.id
    #             self.property_account_payable_id = self.customer_category_id.account_payable_id.id
    #             if self.child_ids:
    #                 for child in self.child_ids:
    #                     child.customer_category_id = self.customer_category_id
    #                     child.property_account_receivable_id = self.customer_category_id.account_receivable_id.id
    #                     child.property_account_payable_id = self.customer_category_id.account_payable_id.id
    #         elif not self.customer_category_id.account_receivable_id.id and self.customer_category_id.account_payable_id.id:
    #             raise ValidationError("Customer Category does not have a valid account receivable")
    #         elif self.customer_category_id.account_receivable_id.id and not self.customer_category_id.account_payable_id.id:
    #             raise ValidationError("Customer Category does not have a valid account payable")
    #         else:
    #             raise ValidationError("Customer Category does not have a valid account receivable nor payable")
    #
    # @api.model
    # def _commercial_fields(self):
    #     """Override the _commercial_fields function to exclude 'vat' field."""
    #     commercial_fields = super(ResPartnerInh, self)._commercial_fields()
    #     commercial_fields.remove('vat')
    #     return commercial_fields

