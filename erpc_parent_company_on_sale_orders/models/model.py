from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    parent_company_id = fields.Many2one('res.partner', string='Parent Company',
                                        compute='_get_parent_ids', store=True)

    @api.depends('partner_id')
    def _get_parent_ids(self):
        for rec in self:
            if rec.partner_id:
                rec.parent_company_id = rec.partner_id.parent_id


class StockMove(models.Model):
    _inherit = 'stock.move'

    parent_company_id = fields.Many2one('res.partner', string='Parent Company',
                                        compute='_get_parent_ids', store=True)

    @api.depends('partner_id')
    def _get_parent_ids(self):
        for rec in self:
            if rec.partner_id:
                rec.parent_company_id = rec.partner_id.parent_id
