from odoo import fields, models, api
from odoo.exceptions import ValidationError


# class Country(models.Model):
#     _inherit = 'res.country'
#
#     code = fields.Char(
#         string='Country Code', size=2,
#         required=False,
#         help='The ISO country code in two chars. \nYou can use this field for quick search.')


# class ProductOfferLine(models.Model):
#     _name = 'product.offer.line'
#     _description = 'Product Offer Line'
#
#     product_id = fields.Many2one('product.template', required=True)
#     list_price = fields.Float('Sales Price', default=1.0, digits='Product Price',
#                               help="Price at which the product is sold to customers.", compute="_compute_list_price",
#                               precompute=True, store=True)
#
#     @api.depends('product_id')
#     def _compute_list_price(self):
#         for line in self:
#             line.list_price = line.product_id.list_price
#
#     discount = fields.Float('Discount (%)', required=True)
#     offer_id = fields.Many2one('product.offer', string="Offer")
#     currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')
#
#     @api.depends('product_id')
#     def _compute_currency_id(self):
#         main_company = self.env['res.company']._get_main_company()
#         for record in self:
#             record.currency_id = record.product_id.company_id.sudo().currency_id.id or main_company.currency_id.id


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    internal_ref = fields.Char(string="Internal Reference")


# class BusinessType(models.Model):
#     _name = 'business.type'
#     _description = 'type_of_business'
#
#     name = fields.Char(string="Name")
#     code = fields.Integer(string="Code")


# class ContactClass(models.Model):
#     _name = 'yoko.class'
#     _description = 'Class'
#
#     name = fields.Char(string="Name", required=True)


# class CustomerCategory(models.Model):
#     _name = 'customer.category'
#     _description = 'customer_category'
#
#     name = fields.Char(string="Name")
#     code = fields.Integer(string="Code")
#     type = fields.Selection([('customer', 'Customer'), ('supplier', 'Supplier')], string='Type')
#     account_payable_id = fields.Many2one('account.account', company_dependent=True,
#                                          string="Account Payable",
#                                          domain="[('account_type', '=', 'liability_payable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
#                                          help="This account will be used instead of the default one as the payable account for the current partner")
#     account_receivable_id = fields.Many2one('account.account', company_dependent=True,
#                                             string="Account Receivable",
#                                             domain="[('account_type', '=', 'asset_receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
#                                             help="This account will be used instead of the default one as the receivable account for the current partner")


# class ResPartnerCity(models.Model):
#     _name = 'res.partner.city'
#     _description = 'City'
#
#     name = fields.Char(required=True)
#     state_id = fields.Many2one("res.country.state", string='State', related="kaza_id.state_id")
#     kaza_id = fields.Many2one('res.partner.kaza', string='Kaza', required=True)


# class ResPartnerKaza(models.Model):
#     _name = 'res.partner.kaza'
#     _description = 'Kaza'
#
#     name = fields.Char(required=True)
#     state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
#                                domain="[('country_id.name', '=', 'Lebanon')]", required=True)


# class ProductBrand(models.Model):
#     # TODO: can be removed after installing yoko_stock
#     _name = 'product.brand'
#     _description = 'product_brand'
#
#     code = fields.Integer(string="Code")
#     name = fields.Char(string="Name")


# class ProductCategory(models.Model):
#     # TODO: can be removed after installing yoko_stock
#     _name = 'product.categories'
#     _description = 'product_categories'
#
#     code = fields.Integer(string="Code")
#     name = fields.Char(string="Name")


# class ProductFamily(models.Model):
#     # TODO: can be removed after installing yoko_stock
#     _name = 'product.family'
#     _description = 'product_family'
#
#     code = fields.Integer(string="Code")
#     name = fields.Char(string="Name")


# class ProductPattern(models.Model):
#     # TODO: can be removed after installing yoko_stock
#     _name = 'product.pattern'
#     _description = 'product_pattern'
#
#     code = fields.Char(string="Code")
#     name = fields.Char(string="Name")


# class ProductType(models.Model):
#     # TODO: can be removed after installing yoko_stock
#     _name = 'product.type'
#     _description = 'product_type'
#
#     code = fields.Integer(string="Code")
#     name = fields.Char(string="Name")


# class ProductSize(models.Model):
#     # TODO: can be removed after installing yoko_stock
#     _name = 'product.size'
#     _description = 'product_size'
#
#     code = fields.Integer(string="Code")
#     name = fields.Char(string="Name")
#     width = fields.Float(string="Width")
#     aspect = fields.Float(string="Aspect")
#     ratio = fields.Float(string="Ratio")
#     inch = fields.Float(string="Inch")


# class ProductSeries(models.Model):
#     # TODO: can be removed after installing yoko_stock
#     _name = 'product.series'
#     _description = 'product_series'
#     code = fields.Integer(string="Code")
#     name = fields.Char(string="Name")


# class ResPartnerDiscount(models.Model):
#     _name = 'res.partner.discount'
#     _description = 'new model that handel many discounts in contacts'
#
#     partner_id = fields.Many2one('res.partner', string='Partner', domain="[('is_driver', '=', False)]")
#     # brand_id = fields.Many2one('product.brand', string='Brand')
#     price_list_id = fields.Many2one('product.pricelist', string='Price List')


# class LostReason(models.Model):
#     _name = "sale.lost.reason"
#     _description = 'sale Lost Reason'
#
#     name = fields.Char('Description', required=True, translate=True)
#     active = fields.Boolean('Active', default=True)
#     sales = fields.One2many('sale.order', 'cancel_reason', string='Sales', readonly=True)


# class ProductOffer(models.Model):
#     _name = 'product.offer'
#     _description = 'Product Offer'
#
#     name = fields.Char('Name', required=True)
#     # brand_id = fields.Many2one('product.brand', string='Brand', )
#     offer_line_ids = fields.One2many('product.offer.line', 'offer_id')
#     active = fields.Boolean('Active', default=True)

    # def create(self, vals):
    #     if not self.env.user.has_group('yoko_customization.offer_access_cus'):
    #         raise ValidationError(
    #             'You do not have create access\nPlease contact your administrator!\nGroup: Offer Access')
    #     return super().create(vals)
    #
    # def write(self, vals):
    #     if not self.env.user.has_group('yoko_customization.offer_access_cus'):
    #         raise ValidationError(
    #             'You do not have edit access\nPlease contact your administrator!\nGroup: Offer Access')
    #     return super().write(vals)
    #
    # def unlink(self):
    #     if not self.env.user.has_group('yoko_customization.offer_access_cus'):
    #         raise ValidationError(
    #             'You do not have delete access\nPlease contact your administrator!\nGroup: Offer Access')
    #     return super().unlink()


class ProductCategoryInh(models.Model):
    _inherit = 'product.category'

    advertising = fields.Boolean("Advertising Department")


# class ResDriver(models.Model):
#     _name = 'res.partner.driver'
#     _description = 'Driver'
#
#     active = fields.Boolean('Active', default=True)
#     name = fields.Char(string="Name")
#     code = fields.Char(string="Code")
#     description = fields.Text(string='Description')
#     notes = fields.Text(string='Notes')
