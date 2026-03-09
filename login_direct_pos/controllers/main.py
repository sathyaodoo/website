# -*- coding: utf-8 -*-

import odoo
import datetime
import ast
import logging
import json

from odoo.http import request, route
from odoo import http, _, fields
from markupsafe import Markup

from odoo.exceptions import UserError
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.utils import ensure_db
from odoo.addons.website.controllers.main import Website
from odoo.addons.auth_oauth.controllers.main import OAuthLogin
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController
from odoo.addons.website_sale.controllers.product_configurator import ( WebsiteSaleProductConfiguratorController)

CREDENTIAL_PARAMS = ['login', 'password', 'type']

_logger = logging.getLogger(__name__)


class WebsiteFAQ(http.Controller):

    @http.route(['/faq'], type='http', auth='public', website=True)
    def website_faq(self, **kwargs):

        faqs = request.env['faq.model'].sudo().search([
            ('active', '=', True)
        ])
        print(faqs)
        return request.render('login_direct_pos.website_faq', {
            'faqs': faqs
        })


class AlanShops(http.Controller):

    # @route(['/shop/brands', '/shop/brands/page/<int:page>'], type='http', auth="public", website=True)
    # def BrandPage(self, page=0):
    #     domain = ['&',('active','=',True), ('website_id', 'in', (False, request.website.id))]
    #     brands = request.env['as.product.brand'].sudo().search(domain, order="name asc")
    #     total = brands.sudo().search_count([])
    #     pager = request.website.pager(
    #         url='/shop/brands',
    #         total=total,
    #         page=page,
    #         step=30,
    #     )
    #     offset = pager['offset']
    #     brands = brands[offset: offset + 30]
    #     return request.render("theme_alan.brand_list", {'brands':brands, 'pager': pager})

    def format_amount(self, amount):
        price_list = request.env['website'].get_current_website().pricelist_ids.sudo().currency_id
        for i in price_list:
            return f"{i.symbol} {amount:.2f}"

    @route('/get_mini_cart', auth='public', type="json", website=True)
    def mini_cart(self, **kw):
        website = request.env['website'].get_current_website()
        order = request.cart
        _logger.info(order,'>>>>>>>>>>>>>')
        suggested_products = order.sudo()._cart_accessories()
        # as_free_shipping_details = order.sudo().get_shipping_details()
        # Product lines
        def format_product_line(line):
            print(line.get_description_following_lines(),'>>>>>>>>>>>>>')
            return {
                'line_id': line.id,
                'product_id': line.product_id.id,
                'product_tmp_id': line.product_id.product_tmpl_id.id,
                'image_url': f"/web/image/product.product/{line.product_id.id}/image_512",
                'website_url': line.product_id.website_url,
                'discount': line.discount,
                'price_total': line.price_total,
                'display_name': line.product_id.with_context(display_default_code=False).display_name,
                'product_uom_qty': line.product_uom_qty,
                'description_sale': line.get_description_following_lines(),
                'formated_amount': self.format_amount(line.price_total),
            }

        # Suggested Product lines
        def format_suggested_product_line(prod):
            combination_info = prod._get_combination_info_variant()
            return {
                'product_id': prod.id,
                'product_name': prod.name,
                'has_discounted_price': combination_info['has_discounted_price'],
                'list_price': self.format_amount(combination_info['list_price']),
                'price': self.format_amount(combination_info['price']),
                'image_url': f"/web/image/product.product/{prod.id}/image_512",
                'website_url': prod.website_url,
            }

        website_order_lines = [format_product_line(line) for line in order.website_order_line]
        suggested_products_lines = [format_suggested_product_line(prod) for prod in suggested_products]

        # Cart summary
        cart_summary = {
            # 'reward_amount': self.format_amount(order.reward_amount) if order.reward_amount else 0,
            'carrier_id': order.carrier_id.id,
            'amount_delivery': self.format_amount(order.amount_delivery),
            'amount_untaxed': self.format_amount(order.amount_untaxed),
            'amount_tax': self.format_amount(order.amount_tax),
            'amount_total': self.format_amount(order.amount_total),
            'shipping_detail': {}
        }
        # if as_free_shipping_details:
        #     cart_summary.update({
        #         'shipping_detail': {
        #             'any_ns_product': as_free_shipping_details['any_ns_product'],
        #             'carries_amount': as_free_shipping_details['carries_amount'],
        #             'total_amount':as_free_shipping_details['total_amount'],
        #             'status': as_free_shipping_details['status'],
        #             'pending_amount': self.format_amount(as_free_shipping_details['pending_amount']),
        #             'active_free_shipping': request.website.active_free_shipping,
        #             }
        #         })

        context = {
            'cart_quantity': order.cart_quantity,
            'website_order_lines': website_order_lines,
            'suggested_products': suggested_products_lines,
            'cart_summary': cart_summary
        }
        return context

    @route('/as_clear_cart', type="json", auth="public", website=True)
    def as_clear_cart(self, **kw):
        order = request.cart
        request.session['website_sale_cart_quantity'] = 0
        order.unlink()

    @route('/as_get_quick_view_templates', type="json", auth="public", website=True)
    def get_rating_template(self, **kw):

        website = request.website
        product_tmpl_id = request.env['product.template'].sudo().browse(kw.get('product_tmpl_id'))
        product_id = request.env['product.product'].sudo().browse(kw.get('product_id'))

        # Rating
        review_count = product_tmpl_id.rating_count
        rating_text = ("%d reviews" % review_count) if review_count > 1 else "%d review" % review_count

        # categories
        categories = product_tmpl_id.public_categ_ids.filtered(lambda x: x.website_id == website or not x.website_id).mapped('name')
        print(categories,'>>>>>>>>>>>>>')
        category_template = f"<div class='as-pd-cat-list as-pd-lists'><label>Category: </label> <span>{', '.join(categories)}</span></div>" if categories and website.active_product_category else ""

        # SKU Template
        sku_template = f" <div class='as_product_sku as-pd-lists'><label>SKU: </label><span>{product_id.default_code}</span></div>" if product_id.default_code and website.active_product_reference else ""

        # Bulk save view
        bulk_save_view = ""
        current_pricelist = website._get_current_pricelist()
        if current_pricelist:
            pricelist_item_ids = current_pricelist.sudo()._get_applicable_rules(product_id, fields.Date.today())
            if website.active_product_bulk_save and pricelist_item_ids:
                bulk_save_view = request.env['ir.ui.view']._render_template(
                    "theme_alan.bulk_save_offers", {'product': product_tmpl_id, 'pricelist_item_ids': pricelist_item_ids}
                )

        # Product comparison
        comparison_view = website.is_view_active('website_sale_comparison.product_add_to_compare')
        product_variant_id = product_tmpl_id.sudo()._get_first_possible_variant_id()
        show_compare = bool(categories and product_variant_id and comparison_view)
        render_if_active = website.is_view_active

        # Product Advance Info
        offer_ids = product_tmpl_id.product_offer_ids
        advance_info = {}

        for offer in offer_ids:
            if offer.types == 'offer' and website.active_product_advance_info:
                advance_info[offer.id] = {
                    'id':offer.id,
                    'name': offer.name,
                    'short_description': offer.short_description,
                    'icon': offer.icon
                }
        values = {
            'rating_template': render_if_active('website_sale.product_comment') and request.env['ir.ui.view']._render_template(
                "portal_rating.rating_widget_stars_static", {'rating_avg': product_tmpl_id.rating_avg, 'rating_count': rating_text}
            ) or "",
            'sale_count': product_id.get_sale_count_last_month(),
            'bulk_save_view': bulk_save_view,
            'show_compare': show_compare,
            'show_wishlist': render_if_active('website_sale_wishlist.product_add_to_wishlist'),
            'show_buy_now': render_if_active('website_sale.product_buy_now'),
            'category_template': category_template,
            'sku_template': sku_template,
            'tag_template': render_if_active('website_sale.product_tags') and request.env['ir.ui.view']._render_template(
                "website_sale.product_tags", {'all_product_tags': product_id.all_product_tag_ids}
            ) or "",
            'brand_template': request.env['ir.ui.view']._render_template("theme_alan.as_product_brand_info", {'product': product_tmpl_id}),
            'active_b2b_mode': bool(website.active_b2b_mode and request.env.user._is_public()) ,
            'active_login_popup': website.active_login_popup,
            'active_offer_timer': website.active_product_offer_timer,
            'offer_timing': product_id._get_offer_timing(website._get_current_pricelist()),
            'advance_info':advance_info
        }

        return values

    # @route('/get_alan_configuration', auth='public', type="json", website=True)
    # def get_alan_configuration(self, **kw):
    #     website = request.website
    #     data = {
    #         'active_login_popup':website.active_login_popup,
    #         'active_mini_cart':website.active_mini_cart,
    #         'active_scroll_top':website.active_scroll_top,
    #         'active_b2b_mode':website.active_b2b_mode,

    #         'active_shop_quick_view': website.active_shop_quick_view,
    #         'active_shop_rating': website.active_shop_rating,
    #         'active_shop_similar_product': website.active_shop_similar_product,
    #         'active_shop_offer_timer': website.active_shop_offer_timer ,
    #         'active_shop_color_variant': website.active_shop_color_variant,
    #         'active_shop_stock_info': website.active_shop_stock_info,
    #         'active_shop_brand_info': website.active_shop_brand_info,
    #         'active_shop_hover_image':website.active_shop_hover_image,
    #         'active_shop_label':website.active_shop_label,
    #         'active_shop_clear_filter':website.active_shop_clear_filter,
    #         'active_shop_ppg':website.active_shop_ppg,
    #         'active_stock_only':website.active_stock_only,
    #         'active_load_more':website.active_load_more,
    #         'active_brand_filter':website.active_brand_filter,
    #         'active_rating_filter':website.active_rating_filter,
    #         'active_attribute_count':website.active_attribute_count,
    #         'active_attribute_search':website.active_attribute_search,
    #         'active_hide_zero_attribute':website.active_hide_zero_attribute,
    #         'active_shop_product_reference':website.active_shop_product_reference,

    #         'active_product_label':website.active_product_label,
    #         'active_product_offer_timer':website.active_product_offer_timer,
    #         'active_product_reference':website.active_product_reference,
    #         'active_product_category':website.active_product_category,
    #         'active_product_brand':website.active_product_brand,
    #         'active_product_advance_info':website.active_product_advance_info,
    #         'active_product_variant_info':website.active_product_variant_info,
    #         'active_product_accessory':website.active_product_accessory,
    #         'active_product_alternative':website.active_product_alternative,
    #         'active_product_pager':website.active_product_pager,
    #         'active_product_sticky':website.active_product_sticky,
    #         'active_product_bulk_save':website.active_product_bulk_save,
    #         'active_last_month_count': website.active_last_month_count,
    #         'active_product_inquiry': website.active_product_inquiry,
    #         'active_product_discount': website.active_product_discount,
    #         'active_free_shipping':website.active_free_shipping,
    #     }
    #     return data

    # @route('/set_alan_configuration', auth='public', type="json", website=True)
    # def set_alan_configuration(self, is_active, setting):
    #     request.website.write({ setting: is_active })
    #     return True

    # @route('/get_advance_info', auth='public', type="json", website=True)
    # def get_advance_info(self, advance_info_id):
    #     offer = request.env['as.product.extra.info'].sudo().search([('id','=',advance_info_id)], limit=1)
    #     if offer.detail_description:
    #         return offer.detail_description
    #     return ""

# class WebsiteSaleStockProductConfiguratorController(WebsiteSaleProductConfiguratorController):


# class B2BWebsite(Website):
#     @route()
#     def autocomplete(self, search_type=None, term=None, order=None, limit=5, max_nb_chars=999, options=None):
#         result = super().autocomplete(search_type, term, order, limit, max_nb_chars, options)
#         if request.env.user._is_public() and request.website.active_b2b_mode:
#             result['parts']['is_b2b_mode'] = True
#         else:
#             result['parts']['is_b2b_mode'] = False
#         return result
#     @route()
#     def hybrid_list(self, page=1, search='', search_type='all', **kw):
#         result = super().hybrid_list(page, search, search_type, **kw)
#         if request.env.user._is_public() and request.website.active_b2b_mode:
#             result.qcontext['is_b2b_mode'] = True
#         else:
#             result.qcontext['is_b2b_mode'] = False
#         return result


# class FAQController(http.Controller):

#     @http.route('/faq', type='http', auth="public", website=True)
#     def faq(self, **kwargs):
#         faqs = request.env['faq'].sudo().search([('active', '=', True)])
#         return request.render(
#             'login_direct_pos.faq_template_view',
#             {'faqs': faqs}
#         )
