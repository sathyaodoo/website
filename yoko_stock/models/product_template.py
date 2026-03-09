# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import re
from odoo.osv import expression


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    available_quant = fields.Float(
        compute="_get_available_quantity",
        help="The amount of the product inside the Main Location",
    )
    # family_id = fields.Many2one("product.family", string="Family", required=False)
    # brand_id = fields.Many2one("product.brand", string="Brand", required=False)
    # type_id = fields.Many2one("product.type", string="Type", required=False)
    # category_id = fields.Many2one("product.categories", string="Category", required=False)
    # series_id = fields.Many2one("product.series", string="Series", required=False)
    # pattern_id = fields.Many2one("product.pattern", string="Pattern", required=False)
    # size_id = fields.Many2one("product.size", string="Size")

    # fast_moving = fields.Boolean("Fast Moving Item")

    # liters = fields.Float(string="Liters")
    # cbm = fields.Float(string="Cbm")

    # country_id = fields.Many2one("res.country", "Origin")
    supplier_nb = fields.Char("Supplier Art Number")

    # dolphin = fields.Float(string="Dolphin Item ID")
    # item_code = fields.Char("Old Item Code")
    # kind_id = fields.Many2one("product.type", string="Kind", required=False, help="Kind is the product type")
    # category_id = fields.Many2one('product.categories', string="Classification", required=True)
    # classification_id = fields.Many2one(
    #     "product.categories",
    #     string="Classification",
    #     required=False,
    #     help="Classification is the product category",
    # )

    # search_default_code = fields.Char(
    #     string="Search default code",
    #     compute="_remove_symbol_default_code",
    #     inverse="_inverse_remove_symbol_default_code",
    #     store=True,
    # )

    # size_name = fields.Char(string="Size Name")
    # size_width = fields.Float(string="Width")
    # size_aspect = fields.Float(string="Aspect")
    # size_inch = fields.Char(string="Inch")
    # is_service = fields.Boolean(compute='_compute_is_service', store=True)

    retail_price = fields.Float("Retail Price")

    def _get_default_category_id(self):
        if self.env.user.has_group("yoko_security_custom.advertising_department"):
            return self.env.ref("yoko_stock.product_category_promotion")

    categ_id = fields.Many2one(default=_get_default_category_id)
    advertising = fields.Boolean("Advertising Product", related="categ_id.advertising", store=True)

    # erpc_free_qty = fields.Float('Free To Use Quantity', digits='Product Unit of Measure', compute='_compute_erpc_free_qty')

    # def _compute_erpc_free_qty(self):
    #     for rec in self:
    #         rec.erpc_free_qty = sum(rec.product_variant_ids.mapped('free_qty')) if rec.product_variant_ids else 0

    # @api.depends('type')
    # def _compute_is_service(self):
    #     for product_template in self:
    #         product_template.is_service = product_template.type == 'service'

    # @api.depends("name")
    # def _remove_symbol_default_code(self):
    #     for rec in self:
    #         search_default_code = ""
    #         if rec.name:
    #             search_default_code = "".join(re.findall(r"\d+", rec.name))
    #         rec.search_default_code = search_default_code

    # @api.depends("name")
    # def _inverse_remove_symbol_default_code(self):
    #     pass

    def _get_available_quantity(self):
        for rec in self:
            main_location_id = self.env["stock.location"].sudo().search([
                ("is_main_location", "=", True)
            ])
            rec.available_quant = 0
            if main_location_id:
                quantity = self.env["stock.quant"].sudo().search([
                    ("location_id", "=", main_location_id.id),
                    ("product_id", "=", rec.product_variant_id.id),
                ])
                if quantity:
                    rec.available_quant = sum(quantity.mapped("available_quantity"))
