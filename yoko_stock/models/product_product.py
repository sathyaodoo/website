from odoo import models, fields, api
import re
from odoo.osv import expression


class ProductsProduct(models.Model):
    _inherit = 'product.product'

    available_quant_location_1 = fields.Float(string="NEW Av. Qty", compute="_compute_available_quants")
    available_quant_location_2 = fields.Float(string="DOT Av. Qty", compute="_compute_available_quants")

    @api.depends('name')
    def _compute_available_quants(self):
        for rec in self:
            available_quant_new = 0
            location_id_1 = self.env["stock.location"].sudo().search([("id", "=", 8)])
            if location_id_1:
                quantity = self.env["stock.quant"].sudo().search([
                    ("location_id", "=", location_id_1.id),
                    ("product_id", "=", rec.id),
                    "|",
                    ("lot_id", "=", False),
                    ("is_lot_dot", "=", False),
                ])
                available_quant_new = sum(quantity.mapped("available_quantity"))

            available_quant_dot = 0
            location_id_2 = self.env["stock.location"].sudo().search([("id", "=", 8)])
            if location_id_2:
                quantity = self.env["stock.quant"].sudo().search([
                    ("location_id", "=", location_id_2.id),
                    ("product_id", "=", rec.id),
                    ("is_lot_dot", "=", True),
                ])
                available_quant_dot = sum(quantity.mapped("available_quantity"))

            rec.available_quant_location_1 = available_quant_new
            rec.available_quant_location_2 = available_quant_dot

    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None, order=None):
    #     if not args:
    #         args = []
    #     if name:
    #         positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
    #         product_ids = []
    #         if operator in positive_operators:
    #             product_ids = list(
    #                 self._search([('search_default_code', '=', name)] + args, limit=limit,
    #                              access_rights_uid=name_get_uid))
    #             if not product_ids:
    #                 product_ids = list(
    #                     self._search([('barcode', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid))
    #
    #         if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
    #             product_ids = list(self._search(args + [('search_default_code', operator, name)], limit=limit))
    #             if not limit or len(product_ids) < limit:
    #                 # we may underrun the limit because of dupes in the results, that's fine
    #                 limit2 = (limit - len(product_ids)) if limit else False
    #                 product2_ids = self._search(args + [('name', operator, name), ('id', 'not in', product_ids)],
    #                                             limit=limit2, access_rights_uid=name_get_uid)
    #                 product_ids.extend(product2_ids)
    #         elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
    #             domain = expression.OR([
    #                 ['&', ('search_default_code', operator, name), ('name', operator, name)],
    #                 ['&', ('search_default_code', '=', False), ('name', operator, name)],
    #             ])
    #             domain = expression.AND([args, domain])
    #             product_ids = list(self._search(domain, limit=limit, access_rights_uid=name_get_uid))
    #         if not product_ids and operator in positive_operators:
    #             ptrn = re.compile('(\[(.*?)\])')
    #             res = ptrn.search(name)
    #             if res:
    #                 product_ids = list(self._search([('search_default_code', '=', res.group(2))] + args, limit=limit,
    #                                                 access_rights_uid=name_get_uid))
    #         if not product_ids and self._context.get('partner_id'):
    #             suppliers_ids = self.env['product.supplierinfo']._search([
    #                 ('name', '=', self._context.get('partner_id')),
    #                 '|',
    #                 ('product_code', operator, name),
    #                 ('product_name', operator, name)], access_rights_uid=name_get_uid)
    #             if suppliers_ids:
    #                 product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit,
    #                                            access_rights_uid=name_get_uid)
    #     else:
    #         product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
    #     return product_ids
