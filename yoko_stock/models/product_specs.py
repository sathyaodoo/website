from odoo import fields, models, _, api


# class ProductBrand(models.Model):
#     _name = 'product.brand'
#     _description = 'product_brand'
#
#     code = fields.Integer(string="Code")
#     name = fields.Char(string="Name")

# class StockValuationLayer(models.Model):
#     _inherit = 'stock.valuation.layer'
#     brand_id = fields.Many2one(
#         comodel_name='product.brand', related="product_id.brand_id",
#         string='Brand',store=True,
#         required=False)
#
#     kind_id = fields.Many2one(
#         comodel_name='product.type', related="product_id.kind_id",
#         string='Kind', store=True,
#         required=False)
#
#     product_qty_by_liter = fields.Float(string="Quantity by Liters",compute="_compute_qty_by_liter", readonly=True)
#
#     def _compute_qty_by_liter(self):
#         for record in self:
#             record.product_qty_by_liter = record.quantity * record.product_id.factor

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # brand_id = fields.Many2one(
    #     comodel_name='product.brand', related="product_id.brand_id",
    #     string='Brand',store=True,
    #     required=False)

    is_product_quantity_manager = fields.Boolean('Is Product Quantity Manager', compute='_compute_pqm')

    def _compute_pqm(self):
        for rec in self:
            if self.env.user.has_group("yoko_stock.set_quantity_products"):
                rec.is_product_quantity_manager = True
            else:
                rec.is_product_quantity_manager = False

    # @api.model
    # def _get_quants_action(self, domain=None, extend=False):
    #     """ Returns an action to open (non-inventory adjustment) quant view.
    #     Depending of the context (user have right to be inventory mode or not),
    #     the list view will be editable or readonly.
    #
    #     :param domain: List for the domain, empty by default.
    #     :param extend: If True, enables form, graph and pivot views. False by default.
    #     """
    #     if not self.env['ir.config_parameter'].sudo().get_param('stock.skip_quant_tasks'):
    #         self._quant_tasks()
    #     ctx = dict(self.env.context or {})
    #     ctx['inventory_report_mode'] = True
    #     ctx.pop('group_by', None)
    #     action = {
    #         'name': _('Locations'),
    #         'view_mode': 'list,form',
    #         'res_model': 'stock.quant',
    #         'type': 'ir.actions.act_window',
    #         'context': ctx,
    #         'domain': domain or [],
    #         'help': """
    #             <p class="o_view_nocontent_empty_folder">{}</p>
    #             <p>{}</p>
    #             """.format(_('No Stock On Hand'),
    #                        _('This analysis gives you an overview of the current stock level of your products.')),
    #     }
    #
    #     target_action = self.env.ref('stock.dashboard_open_quants', False)
    #     if target_action:
    #         action['id'] = target_action.id
    #
    #     form_view = self.env.ref('stock.view_stock_quant_form_editable').id
    #     # if self.env.context.get('inventory_mode') and self.user_has_groups('stock.group_stock_manager'):
    #     # action['view_id'] = self.env.ref('stock.view_stock_quant_tree_editable').id
    #     # else:
    #     action['view_id'] = self.env.ref('stock.view_stock_quant_tree_inventory_editable').id
    #     action.update({
    #         'views': [
    #             (action['view_id'], 'list'),
    #             (form_view, 'form'),
    #         ],
    #     })
    #     if extend:
    #         action.update({
    #             'view_mode': 'tree,form,pivot,graph',
    #             'views': [
    #                 (action['view_id'], 'list'),
    #                 (form_view, 'form'),
    #                 (self.env.ref('stock.view_stock_quant_pivot').id, 'pivot'),
    #                 (self.env.ref('stock.stock_quant_view_graph').id, 'graph'),
    #             ],
    #         })
    #     return action


# class ProductCategory(models.Model):
#     _name = 'product.categories'
#     _description = 'product_categories'
#
#     code = fields.Integer(string="Code")
#     name = fields.Char(string="Name")


# class ProductFamily(models.Model):
#     _name = 'product.family'
#     _description = 'product_family'
#
#     code = fields.Integer(string="Code")
#     name = fields.Char(string="Name")


# class ProductPattern(models.Model):
#     _name = 'product.pattern'
#     _description = 'product_pattern'
#
#     code = fields.Char(string="Code")
#     name = fields.Char(string="Name")


# class ProductType(models.Model):
#     _name = 'product.type'
#     _description = 'product_type'
#
#     code = fields.Integer(string="Code")
#     name = fields.Char(string="Name")


# class ProductSize(models.Model):
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
#     _name = 'product.series'
#     _description = 'product_series'
#     code = fields.Integer(string="Code")
#     name = fields.Char(string="Name")
