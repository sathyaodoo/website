from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError, UserError, AccessError
import logging


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    sale_id = fields.Many2one('sale.order', string='Sale Order', compute='_compute_sale_id', store=True)
    # parent_id = fields.Many2one('res.partner', string='Parent', related='picking_id.parent_company_id', store=True)
    user_id = fields.Many2one('res.partner', string='Customer', related='picking_id.partner_id', store=True)
    invoice = fields.Many2many('account.move', string='invoice', related='sale_id.invoice_ids')

    def _compute_sale_id(self):
        for line in self:
            sale_id = self.env['sale.order'].search([('name', '=', line.origin)])
            if sale_id:
                line.sale_id = sale_id.id
            else:
                line.sale_id = False


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    promotional_categ = fields.Many2one(
        comodel_name='product.category', store=False,
        string='Promtional Category',
        default=lambda self: self.env['product.category'].search([('is_promotional_categ', '=', True)], limit=1))

    name = fields.Char(
        string="Order Reference",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))

    delivery_state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('waiting', 'Waiting Another Operation'),
            ('confirmed', 'Waiting'),
            ('assigned', 'Ready'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ],
        string='Delivery Status',
        compute='_compute_delivery_state_erpc',
        store=True
    )

    @api.depends('picking_ids')
    def _compute_delivery_state_erpc(self):
        for order in self:
            if order.picking_ids:
                order.delivery_state = order.picking_ids[0].state
            else:
                order.delivery_state = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_promo', False):
                vals['quotation_type'] = 'promotional_quotation'
                if not self.env.user.has_group('yoko_security_custom.advertising_department'):
                    raise ValidationError("You do not Have access to update Promotional Quotation")
                if vals.get('name', _('New')) == _('New'):
                    seq_date = None
                    if 'date_order' in vals:
                        seq_date = fields.Datetime.context_timestamp(self,
                                                                     fields.Datetime.to_datetime(vals['date_order']))
                    vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.promo',
                                                                        sequence_date=seq_date) or _('New')

        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        for record in self:
            if record.is_promo and not self.env.user.has_group('yoko_security_custom.advertising_department'):
                raise ValidationError("You do not Have access to update Promotional Quotation")
            else:
                return super().write(vals)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('product_id', 'product_uom_id', 'product_uom_qty')
    def _compute_price_unit(self):
        for line in self:
            if line.product_id.categ_id.is_promotional_categ:
                line.price_unit = 0
            else:
                super()._compute_price_unit()


class ProductTemplate(models.Model):
    _inherit = "product.category"

    is_promotional_categ = fields.Boolean(
        string='Is Promotional Categ',
        required=False)