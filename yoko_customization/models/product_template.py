# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import re


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    # offer_id = fields.Many2one('product.offer', compute="_get_offer_id")
    show_price_after_discount = fields.Boolean(string="Show Price After Discount")

    # @api.depends('name')
    # def _remove_symbol_default_code(self):
    #     for rec in self:
    #         search_default_code = ''
    #         if rec.name:
    #             search_default_code = "".join(re.findall(r"\d+", rec.name))
    #         rec.search_default_code = search_default_code

    # @api.depends('name')
    # def _inverse_remove_symbol_default_code(self):
    #     pass

    def _get_available_quantity(self):
        for rec in self:
            main_location_id = self.env['stock.location'].sudo().search([('is_main_location', '=', True)])
            rec.available_quant = 0
            if main_location_id:
                quantity = self.env['stock.quant'].sudo().search([
                    ('location_id', '=', main_location_id.id), ('product_id', '=', rec.product_variant_id.id)])
                if quantity:
                    rec.available_quant = sum(quantity.mapped('available_quantity'))

    # def _get_offer_id(self):
    #     for rec in self:
    #         line_id = self.env['product.offer.line'].search([('product_id', '=', rec.id),('offer_id.active','=',True)],
    #                                                         order="create_date desc", limit=1)
    #         if line_id:
    #             rec.offer_id = line_id.offer_id.id
    #         else:
    #             rec.offer_id = False
