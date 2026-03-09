from odoo import fields, models, api
import logging

logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    sale_id = fields.Many2one('sale.order', string='Sale Order', compute='_compute_sale_id', store=True)
    parent_id = fields.Many2one('res.partner', string='Parent', related='sale_id.partner_id.parent_id')
    user_id = fields.Many2one('res.partner', string='Customer', related='sale_id.partner_id')
    invoice = fields.Many2many('account.move', string='invoice', related='sale_id.invoice_ids')

    def _compute_sale_id(self):
        for line in self:
            sale_id = self.env['sale.order'].search([('name', '=', line.origin)])
            if sale_id:
                line.sale_id = sale_id.id
            else:
                line.sale_id = False
