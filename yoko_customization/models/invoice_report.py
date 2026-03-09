# from odoo import fields, models, api
# from odoo.addons.account.models.account_move import PAYMENT_STATE_SELECTION
#
#
# class DiscountSaleReport(models.Model):
#     _inherit = 'sale.report'
#
#     family_id = fields.Many2one('product.family', string='Family', readonly=True)
#     brand_id = fields.Many2one('product.brand', string='Brand', readonly=True)
#     size_name = fields.Char(string='Size', readonly=True)
#     parent_id = fields.Many2one('res.partner', string='Parent', readonly=True, domain="[('is_driver', '=', False)]")
#     country_of_origin = fields.Many2one('res.country', string='Country of Origin', readonly=True)
#
#
#     def _select_additional_fields(self):
#         res = super()._select_additional_fields()
#         res['family_id'] = "t.family_id"
#         res['brand_id'] = "t.brand_id"
#         res['size_name'] = "t.size_name"
#         res['country_of_origin'] = "t.country_of_origin"
#         res['parent_id'] = "partner.parent_id"
#         return res
#
#     def _group_by_sale(self):
#         res = super()._group_by_sale()
#         res += """,
#             t.family_id,
#             t.brand_id,
#             t.size_name,
#             t.country_of_origin,
#             partner.parent_id
#             """
#         return res
#
#
# class AccountInvoiceReport(models.Model):
#     _inherit = 'account.invoice.report'
#     factor = fields.Float(string='Factor', readonly=True)
#     family_id = fields.Many2one('product.family', string='Family', readonly=True)
#     brand_id = fields.Many2one('product.brand', string='Brand', readonly=True)
#     size_name = fields.Char(string='Size', readonly=True)
#     parent_company_id = fields.Many2one('res.partner', string='Parent', readonly=True)
#     kind_id = fields.Many2one('product.type', string='Kind', readonly=True)
#     purchase_price = fields.Float(
#         string='Unit Cost',
#         readonly=True)
#
#     total_cost = fields.Float(string="Total Cost", readonly=True)
#
#     gross_margin_profit = fields.Float(string="GMP", readonly=True)
#     product_qty_by_liter = fields.Float(string="Product Qty by Liters", readonly=True)
#
#     partner_tax_id = fields.Char(string='Tax ID', readonly=True)
#     state_id = fields.Many2one(
#         comodel_name='res.country.state',
#         string='Region',
#         readonly=True)
#
#     kaza_id = fields.Many2one(
#         comodel_name='res.partner.kaza',
#         string='Kazaa',
#         readonly=True)
#
#     city_id = fields.Many2one(
#         comodel_name='res.partner.city',
#         string='City',
#         readonly=True)
#
#     driver_id = fields.Many2one(
#         comodel_name='res.partner',
#         string='Driver',
#         readonly=True)
#
#     narration = fields.Html(string="Description")
#     customer_class_id = fields.Many2one(comodel_name="yoko.class", string="Class")
#     customer_category_id = fields.Many2one(comodel_name="customer.category", string="Customer Category")
#
#     standard_price = fields.Float(string="Current Price", readonly=True)
#     sales_price = fields.Float(string="Sale Price", readonly=True)
#     price_list_id = fields.Many2one(comodel_name="product.pricelist", string="Client Discount", readonly=True)
#
#     discount = fields.Float(string="Discount", readonly=True)
#     final_price = fields.Float(string="Final Price", readonly=True)
#     amount_tax = fields.Float(string="Tax Amount", readonly=True)
#     create_uid = fields.Many2one(string="Created By", comodel_name='res.users', readonly=True)
#     lot_id = fields.Many2one(string="Lot", comodel_name='stock.lot', readonly=True)
#     offer_id = fields.Many2one(string="Offer", comodel_name='product.offer', readonly=True)
#     country_of_origin = fields.Many2one('res.country', string='Country of Origin', readonly=True)
#
#
#     def _select(self):
#         return super()._select() + (",template.country_of_origin as country_of_origin, partner.customer_class_id as customer_class_id,"
#                                     "partner.customer_category_id as customer_category_id,move.narration as narration, move.state_id as state_id, move.kaza_id as kaza_id,"
#                                     "move.city_id as city_id,move.driver_id as driver_id,"
#                                     "Case When move.is_credit_note "
#                                     "then 0 else sale_line.purchase_price * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END) END AS purchase_price,"
#                                     "sale_line.create_uid as create_uid,sale_line.lot_id as lot_id,"
#                                     "move.amount_tax as amount_tax,"
#                                     " move.parent_company_id as parent_company_id,partner.vat as partner_tax_id,"
#                                     "template.factor as factor, template.brand_id as brand_id,"
#                                     " template.family_id as family_id, template.size_name as size_name,"
#                                     " template.list_price as standard_price,template.kind_id as kind_id,"
#                                     "line.discount as discount,sale_line.price_after_discount as sales_price,"
#                                     "line.price_list_id as price_list_id,sale_line.offer_id as offer_id, "
#                                     "(1 - (line.discount / 100)) * line.price_unit as final_price, Case When move.is_credit_note "
#                                     "then 0 else sale_line.purchase_price * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)  * line.quantity END as total_cost,"
#                                     "line.price_subtotal * "
#                                     "(CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)"
#                                     " - (Case When move.is_credit_note or sale_line.purchase_price is NULL Then 0 else sale_line.purchase_price * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)"
#                                     " * line.quantity END) "
#                                     "as gross_margin_profit,"
#                                     " (line.quantity * template.factor * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)) as product_qty_by_liter "
#                                     )
#
#     def _from(self):
#         return super()._from() + (
#             " LEFT JOIN sale_order_line_invoice_rel sale_invoice_line ON sale_invoice_line.invoice_line_id = ("
#             "select MIN(sale_invoice_line.invoice_line_id) from sale_order_line_invoice_rel sale_invoice_line where"
#             " sale_invoice_line.invoice_line_id = line.id limit 1) LEFT JOIN sale_order_line sale_line ON sale_line.id = sale_invoice_line.order_line_id")
#
#
# class SalesInvoiceReport(models.Model):
#     _name = 'sales.invoice.report'
#
#     brand_id = fields.Many2one('product.brand', string='Brand', readonly=True)
#     parent_company_id = fields.Many2one('res.partner', string='Parent', readonly=True)
#
#     partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
#     product_id = fields.Many2one('product.product', string='Product', readonly=True)
#     product_categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
#
#     move_type = fields.Selection([
#         ('out_invoice', 'Customer Invoice'),
#         ('in_invoice', 'Vendor Bill'),
#         ('out_refund', 'Customer Credit Note'),
#         ('in_refund', 'Vendor Credit Note'),
#     ], readonly=True)
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('posted', 'Open'),
#         ('cancel', 'Cancelled')
#     ], string='Invoice Status', readonly=True)
#     payment_state = fields.Selection(selection=PAYMENT_STATE_SELECTION, string='Payment Status', readonly=True)
#     move_id = fields.Many2one('account.move', readonly=True)
#
#     kind_id = fields.Many2one('product.type', string='Kind', readonly=True)
#     quantity = fields.Float(string='Product Quantity', readonly=True)
#     product_qty_by_liter = fields.Float(string="Product Qty by Liters", readonly=True)
#     driver_id = fields.Many2one(comodel_name='res.partner', string='Driver', readonly=True)
#     create_uid = fields.Many2one(string="Created By", comodel_name='res.users', readonly=True)
#     lot_id = fields.Many2one(string="Lot", comodel_name='stock.lot', readonly=True)
#     offer_id = fields.Many2one(string="Offer", comodel_name='product.offer', readonly=True)
#     invoice_date = fields.Date(readonly=True, string="Invoice Date")
#     invoice_user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
#     country_of_origin = fields.Many2one('res.country', string='Country of Origin', readonly=True)
#
#     _depends = {
#         'account.move': [
#             'name', 'state', 'move_type', 'partner_id', 'invoice_user_id', 'fiscal_position_id',
#             'invoice_date', 'invoice_date_due', 'invoice_payment_term_id', 'partner_bank_id',
#         ],
#         'account.move.line': [
#             'quantity', 'price_subtotal', 'price_total', 'amount_residual', 'balance', 'amount_currency',
#             'move_id', 'product_id', 'product_uom_id', 'account_id',
#             'journal_id', 'company_id', 'currency_id', 'partner_id',
#         ],
#         'product.product': ['product_tmpl_id','country_of_origin'],
#         'product.template': ['categ_id'],
#         'uom.uom': ['category_id', 'factor', 'name', 'uom_type'],
#         'res.currency.rate': ['currency_id', 'name'],
#         'res.partner': ['country_id'],
#     }
#
#     @property
#     def _table_query(self):
#         if self.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
#             return '%s %s %s' % (self._select(), self._from(), self._where_full_access())
#
#         return '%s %s %s' % (self._select(), self._from(), self._where())
#
#     @api.model
#     def _select(self):
#         return '''
#             SELECT
#                 line.id,
#                 line.move_id,
#                 line.product_id,
#                 line.company_id,
#                 line.company_currency_id,
#                 move.invoice_user_id,
#                 move.state,
#                 move.move_type,
#                 move.partner_id,
#                 move.payment_state,
#                 move.invoice_date,
#                 template.categ_id AS product_categ_id,
#                 template.country_of_origin as country_of_origin,
#                 line.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END) AS quantity,
#                 move.driver_id as driver_id,
#                     sale_line.create_uid as create_uid,
#                     sale_line.lot_id as lot_id,
#                     move.parent_company_id as parent_company_id,
#                     template.brand_id as brand_id,
#                     template.list_price as standard_price,template.kind_id as kind_id,
#                     line.discount as discount,sale_line.price_after_discount as sales_price,
#                     sale_line.offer_id as offer_id,
#                      (line.quantity * template.factor * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)) as product_qty_by_liter
#
#         '''
#
#     @api.model
#     def _from(self):
#         return '''
#             FROM account_move_line line
#                 LEFT JOIN res_partner partner ON partner.id = line.partner_id
#                 LEFT JOIN product_product product ON product.id = line.product_id
#                 LEFT JOIN account_account account ON account.id = line.account_id
#                 LEFT JOIN product_template template ON template.id = product.product_tmpl_id
#                 LEFT JOIN uom_uom uom_line ON uom_line.id = line.product_uom_id
#                 LEFT JOIN uom_uom uom_template ON uom_template.id = template.uom_id
#                 INNER JOIN account_move move ON move.id = line.move_id
#                 LEFT JOIN res_partner commercial_partner ON commercial_partner.id = move.commercial_partner_id
#                 JOIN {currency_table} ON currency_table.company_id = line.company_id
#
#                 LEFT JOIN sale_order_line_invoice_rel sale_invoice_line ON sale_invoice_line.invoice_line_id =
#                  (select MIN(sale_invoice_line.invoice_line_id) from sale_order_line_invoice_rel sale_invoice_line where
#                 sale_invoice_line.invoice_line_id = line.id limit 1)
#                 LEFT JOIN sale_order_line sale_line ON sale_line.id = sale_invoice_line.order_line_id
#
#         '''.format(
#             currency_table=self.env['res.currency']._get_query_currency_table(conversion_date = fields.Date.today(), company_ids=self.env.companies.ids)
#         )
#
#     @api.model
#     def _where(self):
#         return '''
#             WHERE move.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
#                 AND line.account_id IS NOT NULL
#                 AND line.display_type = 'product'
#                 AND partner.user_id =  {user}
#         '''.format(
#             user=self.env.user.id,
#         )
#
#     def _where_full_access(self):
#         return '''
#                     WHERE move.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
#                         AND line.account_id IS NOT NULL
#                         AND line.display_type = 'product'
#                 '''