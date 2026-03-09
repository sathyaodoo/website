from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError, UserError, AccessError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # product_size = fields.Many2one('product.sizes')

    def write(self, vals):
        # Check if the user belongs to the specified group
        if self.env.user.has_group('erpc_product_size.group_user_marketing'):

            # Check if any field other than image field is being updated
            fields_to_check = ['image_1920']  # Add other fields here if needed
            updated_fields = list(vals.keys())

            if any(field not in fields_to_check for field in updated_fields):
                # Display an error message
                raise AccessError("You are not authorized to change fields other than the image.\nGroup: Marketing")

        return super().write(vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # def write(self, vals):
    #     if not self.env.user.has_group('erpc_product_size.group_user_sale_discount_access'):
    #         updated_fields = list(vals.keys())
    #         if 'discount' in updated_fields:
    #             raise AccessError("You are not authorized to change Discount.\nGroup: Sale Discount Access")
    #
    #     return super().write(vals)

    # @api.onchange('discount')
    # def _onchange_discount_restriction(self):
    #     # Check if the user belongs to the specified group
    #     if not self.env.user.has_group('erpc_product_size.group_user_sale_discount_access'):

    #        raise AccessError("You are not authorized to change Discount.\nGroup: Sale Discount Access")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # def write(self, vals):
    #     if not self.env.user.has_group('erpc_product_size.group_user_invoice_discount_access'):
    #         updated_fields = list(vals.keys())
    #         if 'discount' in updated_fields:
    #             raise AccessError("You are not authorized to change Discount.\nGroup: Invoice Discount Access")
    #
    #     return super().write(vals)

    # @api.onchange('discount')
    # def _onchange_discount_restriction(self):
    #     # Check if the user belongs to the specified group
    #     if not self.env.user.has_group('erpc_product_size.group_user_invoice_discount_access'):

    #        raise AccessError("You are not authorized to change Discount.\nGroup: Invoice Discount Access")


# class ProductSize(models.Model):
#     _name = 'product.sizes'

#     name = fields.Char()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _change_saleperson_with_partner(self):
        for rec in self:
            rec.user_id = rec.partner_id.user_id.id


class Approvals(models.Model):
    _inherit = 'approval.request'
    # productLines = fields.Many2many('product.product', computed='_compute_productLines', string='Product Lines')
    #
    # @api.depends('productLines', 'product_line_ids')
    # def _compute_productLines(self):
    #     for rec in self:
    #         if rec.product_line_ids.product_id:
    #             productLines = rec.product_line_ids.product_id

    productLines = fields.Many2many('product.product', compute='_compute_productLines', string='Product Lines',
                                    store=True)
    amount_char = fields.Char(string="Amount", required=True, store=True)

    @api.depends('product_line_ids.product_id')
    def _compute_productLines(self):
        for rec in self:
            product_ids = rec.product_line_ids.mapped('product_id')
            rec.productLines = product_ids
