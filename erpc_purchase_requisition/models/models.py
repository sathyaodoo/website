from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super().button_confirm()

        for line in self.order_line:
            if line.related_requisition_line_id:
                line.related_requisition_line_id.qty_ordered += line.product_qty

        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    related_requisition_line_id = fields.Many2one('purchase.requisition.line')
    related_requisition_line_name = fields.Many2one(related="related_requisition_line_id.requisition_id", string="BO Ref")

class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    extra_ordered_quantity = fields.Float(compute='_compute_extra_quantity')
    remaining_ordered_quantity = fields.Float(compute='_compute_extra_quantity')

    vendor_id = fields.Many2one('res.partner', related='requisition_id.vendor_id', store=True)
    origin = fields.Char(string='Source Document', related='requisition_id.reference')

    def _compute_extra_quantity(self):
        for record in self:
            po_lines_related = self.env['purchase.order.line'].search([('related_requisition_line_id', '=', record.id),
                                                                       ('order_id.state', 'in', ['purchase', 'done'])])

            tot = 0.0

            for rec in po_lines_related:
                tot += rec.product_qty

            record.extra_ordered_quantity = tot
            record.remaining_ordered_quantity = record.product_qty - tot

    def create_purchase_order_for_selected_lines(self):
        selected_line_ids = self.env.context.get('active_ids', [])

        all_recs_line = self.env['purchase.requisition.line'].search([('id', 'in', selected_line_ids)])

        if len(set(all_recs_line.mapped('requisition_id.vendor_id'))) > 1:
            raise UserError('Please Choose Lines That Has Same Vendor')

        purchase_order = self.env['purchase.order'].create(

            {
                'partner_id': all_recs_line[0].requisition_id.vendor_id.id,
                'currency_id': all_recs_line[0].requisition_id.currency_id.id,
                'picking_type_id': all_recs_line[0].requisition_id.picking_type_id.id,
            })

        for line in selected_line_ids:
            data = self.env['purchase.requisition.line'].browse(line)

            order_line_values = data._prepare_purchase_order_line(
                name=data.product_id.name, product_qty=data.remaining_ordered_quantity, price_unit=data.price_unit,
                taxes_ids=[])

            order_line_values['order_id'] = purchase_order.id
            order_line_values['related_requisition_line_id'] = line
            # order_line_values['requested_quantity'] = data.remaining_ordered_quantity
            self.env['purchase.order.line'].create(order_line_values)

        form_id = self.env.ref("purchase.purchase_order_form").id

        return {
            "name": _("Requests for Quotation"),
            "view_mode": "list,form",
            'views': [(form_id, 'form')],
            "res_model": "purchase.order",
            "type": "ir.actions.act_window",
            "target": "current",
            'res_id': purchase_order.id,
        }


PURCHASE_REQUISITION_STATES = [
    ('draft', 'Draft'),
    ('ongoing', 'Ongoing'),
    ('in_progress', 'Confirmed'),
    ('open', 'Bid Selection'),
    ('done', 'Closed'),
    ('cancel', 'Cancelled')
]


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    state_blanket_order = fields.Selection(PURCHASE_REQUISITION_STATES, compute='_set_state')

    # def _set_state(self):
    #     super()._set_state()
    #     for requisition in self:
    #         if not any(l.remaining_ordered_quantity != 0 for l in requisition.line_ids):
    #             requisition.state = "done"

    total_quantities = fields.Float(compute='compute_total_quants')
    total_amount = fields.Float(compute='compute_total_quants')

    def compute_total_quants(self):
        for rec in self:
            tot = 0.0
            amt = 0.0

            for line in rec.line_ids:
                tot += line.product_qty
                amt += (line.product_qty * line.price_unit)

            rec.total_quantities = tot
            rec.total_amount = amt

    remaining_ordered_quantity = fields.Float(compute='_compute_remaining_quantity')

    def _compute_remaining_quantity(self):

        for record in self:
            record.remaining_ordered_quantity = sum(record.line_ids.mapped('remaining_ordered_quantity'))