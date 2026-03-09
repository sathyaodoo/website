# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


# class MultiSelection(models.TransientModel):
#     _name = 'multi.selection'
#     _description = 'Multi Selection'
#
#     def _default_order(self):
#         return self.env['sale.order'].browse(self._context.get('active_id')).id
#
#     sale_order_id = fields.Many2one('sale.order', default=_default_order)
#     selection_line_ids = fields.One2many('multi.selection.line', 'selection_id')
#
#     # def back_to_select_product(self):
#     #     view = self.env.ref('yoko_customization.multi_selection_view_form')
#     #     return view
#
#     def open_product_selection_wizard(self):
#         view = self.env.ref('yoko_customization.multi_product_form_select')
#         wiz = self.env['select.multi.product'].create({'selection_id': self.id})
#
#         return {
#             'name': _('Select Products'),
#             'type': 'ir.actions.act_window',
#             'res_model': 'select.multi.product',
#             'views': [(view.id, 'form')],
#             'target': 'new',
#             'res_id': wiz.id,
#             'context': self.env.context
#         }
#
#     def move_to_sale_order(self):
#         if not self.selection_line_ids:
#             raise UserError('You must choose at least one product')
#         for rec in self.selection_line_ids:
#             if rec.product_uom_qty < 0:
#                 raise UserError('Quantity can not be negative.')
#         order_line = self.env['sale.order.line']
#         for rec in self.selection_line_ids:
#             line = order_line.create({
#                 "order_id": rec.order_id.id,
#                 "product_uom_qty": rec.product_uom_qty,
#                 "product_id": rec.product_id.id,
#                 'name': rec.product_id.name,
#                 "tax_id": [[6, 0, rec.product_id.taxes_id.ids]] if rec.product_id.taxes_id else None,
#             })
#             line.product_id_change()  # to invoke the changes related to the product change
#
#     def close_multi_selection(self):
#         return {'type': 'ir.actions.act_window_close'}
#

# class MultiSelectionLine(models.TransientModel):
#     _name = 'multi.selection.line'
#     _inherit = 'sale.order.line'
#     _description = 'Product Selection Line'
#     """Will have the same functionality of the Sale order line"""
#
#     selection_id = fields.Many2one('multi.selection')
#     order_id = fields.Many2one('sale.order', related='selection_id.sale_order_id')
#     discount = fields.Float(digits=(12, 2))
#     available_quant = fields.Float(compute="_get_available_quantity",
#                                    help="The amount of the product inside the Main Location")
#
#     # Changes need to be done in order to be able to inherit from s.o.l
#     invoice_lines = fields.Many2many('account.move.line', 'selection_line_invoice_rel', 'selection_line_id',
#                                      'invoice_line_id', )
#
#     _sql_constraints = [
#         ('accountable_required_fields', "CHECK(1=1)", "Missing required fields on accountable sale order line."),
#         ('non_accountable_null_fields', "CHECK(1=1)", "Forbidden values on non-accountable sale order line"),
#     ]
#
#     def _get_available_quantity(self):
#         for rec in self:
#             rec.available_quant = rec.product_template_id.available_quant


# class SelectMultiProduct(models.TransientModel):
#     _name = 'select.multi.product'
#     _description = 'Select Multi Product'
#     """This model will be called from the Selection Wizard not from SO directly"""
#
#     multi_products = fields.Many2many('product.product', string='Product List')
#     selection_id = fields.Many2one('multi.selection', help="Will relate the ")
#
#
#
#     def back_to_select_product(self):
#         view = self.env.ref('yoko_customization.multi_selection_view_form')
#         return {
#             'name': _('Products Selection'),
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'res_model': 'multi.selection',
#             'views': [(view.id, 'form')],
#             'view_id': view.id,
#             'target': 'new',
#             'res_id': self.selection_id.id,
#         }
#
#     def add_multi_products(self):
#         if not self.multi_products:
#             raise UserError('You must choose at least one product')
#
#         view = self.env.ref('yoko_customization.multi_selection_view_form')
#
#         for rec in self:
#             order_line = self.env['multi.selection.line']
#             # acc_id = order_line._default_account()
#             for product in rec.multi_products:
#                 # acc_id = product.property_account_income_id or product.categ_id.property_account_income_categ_id
#                 # price_unit = product.list_price
#
#                 line = order_line.create({
#                     "selection_id": rec.selection_id.id,
#                     "product_id": product.id,
#                     'name': product.name,
#                     # 'price_unit':price_unit,
#                     # 'account_id':acc_id.id,
#                     # "account_analytic_id":product.analyic_account_id.id or None,
#                     # "uom_id":product.uom_id.id,
#                     "tax_id": [[6, 0, product.taxes_id.ids]] if product.taxes_id else None,
#                 })
#                 line.product_id_change()  # to invoke the changes related to the product change
#
#         return {
#             'name': _('Products Selection'),
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'res_model': 'multi.selection',
#             'views': [(view.id, 'form')],
#             'view_id': view.id,
#             'target': 'new',
#             'res_id': self.selection_id.id,
#             'context': self.env.context,
#         }
#
#     def close_multi_product(self):
#         return {'type': 'ir.actions.act_window_close'}


# class SaleOrderCancel(models.TransientModel):
#     _inherit = 'sale.order.cancel'
#
#     cancel_reason_id = fields.Many2one('sale.lost.reason', string='Cancel Reason', required=True)
#     description = fields.Text(string='Description')
#     cancelled_date = fields.Date(string="Cancelled Date", default=fields.Date.today())
#
#     def action_cancel(self):
#         order = self.order_id
#         reason = self.cancel_reason_id
#         description = self.description
#         cancelled_date = self.cancelled_date
#
#         # set the cancel_reason field of the sale.order record
#         if reason and description:
#             order.cancel_reason = reason.id
#             order.description = description
#             order.cancelled_date = cancelled_date
#
#         elif reason and not description:
#             order.cancel_reason = reason.id
#             order.cancelled_date = cancelled_date
#
#         return order.with_context({'disable_cancel_warning': True})._action_cancel()



# class CustomAccountMoveReversal(models.TransientModel):
#     _inherit = 'account.move.reversal'
#
#     is_reversed = fields.Boolean(string='Is Reversed', default=False)
#
#     def _prepare_default_reversal_new(self, move):
#         reverse_date = self.date
#         return {
#             'ref': _('Reversal of: %(move_name)s, %(reason)s', move_name=move.name, reason=self.reason)
#                    if self.reason
#                    else _('Reversal of: %s', move.name),
#             'date': reverse_date,
#             'is_reversed': True,
#             'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
#             'journal_id': self.journal_id.id,
#             'invoice_payment_term_id': None,
#             'invoice_user_id': move.invoice_user_id.id,
#             'auto_post': True if reverse_date > fields.Date.context_today(self) else 'no',
#         }
#
#     def reverse_moves_new(self, is_modify=False):
#         self.ensure_one()
#         moves = self.move_ids
#
#         # Create default values.
#         default_values_list = []
#         for move in moves:
#             default_values_list.append(self._prepare_default_reversal_new(move))
#
#         batches = [
#             [self.env['account.move'], [], True],  # Moves to be cancelled by the reverses.
#             [self.env['account.move'], [], False],  # Others.
#         ]
#         for move, default_vals in zip(moves, default_values_list):
#             is_auto_post = default_vals.get('auto_post') != 'no'
#             is_cancel_needed = not is_auto_post and is_modify
#             batch_index = 0 if is_cancel_needed else 1
#             batches[batch_index][0] |= move
#             batches[batch_index][1].append(default_vals)
#
#         # Handle reverse method.
#         moves_to_redirect = self.env['account.move']
#         for moves, default_values_list, is_cancel_needed in batches:
#             new_moves = moves._reverse_moves(default_values_list, cancel=is_cancel_needed)
#             moves._message_log_batch(
#                 bodies={move.id: _('This entry has been %s', reverse._get_html_link(title=_("reversed"))) for
#                         move, reverse in zip(moves, new_moves)}
#             )
#
#             if is_modify:
#                 moves_vals_list = []
#                 for move in moves.with_context(include_business_fields=True):
#                     data = move.copy_data({'date': self.date})[0]
#                     data['line_ids'] = [line for line in data['line_ids'] if line[2]['display_type'] == 'product']
#                     moves_vals_list.append(data)
#                 new_moves = self.env['account.move'].create(moves_vals_list)
#
#             moves_to_redirect |= new_moves
#
#         self.new_move_ids = moves_to_redirect
#
#         # Create action.
#         action = {
#             'name': _('Reverse Moves'),
#             'type': 'ir.actions.act_window',
#             'res_model': 'account.move',
#         }
#         if len(moves_to_redirect) == 1:
#             action.update({
#                 'view_mode': 'form',
#                 'res_id': moves_to_redirect.id,
#                 'context': {'default_move_type': moves_to_redirect.move_type},
#             })
#         else:
#             action.update({
#                 'view_mode': 'tree,form',
#                 'domain': [('id', 'in', moves_to_redirect.ids)],
#             })
#             if len(set(moves_to_redirect.mapped('move_type'))) == 1:
#                 action['context'] = {'default_move_type': moves_to_redirect.mapped('move_type').pop()}
#         return action
