from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"
    _rec_name = "name"

    original_qty = fields.Float(string="Requested QTY", copy=False, digits=(16, 0))
    original_u_price = fields.Float(string="Requested U-Price", copy=False)
    user_id = fields.Many2one(related="requisition_id.user_id")
    ordering_date = fields.Date(related="requisition_id.date_start")
    date_end = fields.Date(related="requisition_id.date_end")
    qty_ordered = fields.Float(digits=(16, 0))
    related_po_lines = fields.Many2many(
        "purchase.order.line", compute="_get_related_po_lines", precompute=True,
        copy=False,
        store=True
    )

    related_po_lines_received = fields.Many2many(
        "purchase.order.line", compute='_get_related_po_lines_received'
    )

    received_qty = fields.Float(
        string="Received QTY",
        compute="_compute_received_quantity",
        precompute=True,
        copy=False,
        digits=(16, 0),
        store=True
    )

    name = fields.Char(
        string="Name", compute="_compute_name", precompute=True, copy=False
    )

    remaining_price = fields.Float(
        string="Remaining Confirmed Price",
        compute="_compute_remaining_price",
        precompute=True,
        copy=False,
    )

    extra_ordered_quantity = fields.Float(
        compute="_compute_extra_quantity",
        digits=(16, 0),
        precompute=True,
        copy=False,
        store=True,
    )
    remaining_ordered_quantity = fields.Float(
        compute="_compute_remaining_ordered_quantity",
        digits=(16, 0),
        precompute=True,
        copy=False,
        store=True,
    )

    shipped_value = fields.Float(
        string="Shipped Value",
        compute="_compute_shipped_value",
        precompute=True,
        copy=False,
        store=True
    )

    status = fields.Selection(related="requisition_id.state", store=True)

    @api.depends_context('company')
    def _get_related_po_lines(self):
        for record in self:
            related_po_lines = self.env["purchase.order.line"].search(
                [
                    ("related_requisition_line_id", "=", record.id),
                    ("order_id.state", "in", ["purchase", "done"]),
                ]
            )

            record.related_po_lines = related_po_lines

    def _get_related_po_lines_received(self):
        for record in self:
            po_lines_related_received = self.env["purchase.order.line"].search(
                [
                    ("related_requisition_line_id", "=", record.id),
                    ("order_id.state", "in", ["purchase", "done"]),
                    ("qty_received", ">", 0),
                ]
            )

            record.related_po_lines_received = po_lines_related_received

    @api.depends("product_qty", "status", "related_po_lines",
                 "related_po_lines.order_id.picking_ids.state")
    def _compute_received_quantity(self):
        for record in self:
            po_lines_related = self.env["purchase.order.line"].search(
                [
                    ("related_requisition_line_id", "=", record.id),
                    ("order_id.state", "in", ["purchase", "done"]),
                    ("qty_received", ">", 0),
                ]
            )

            total_received_qty = sum(po_lines_related.mapped("qty_received"))
            record.received_qty = total_received_qty

    @api.depends("product_qty", "received_qty", "status", "related_po_lines", "related_po_lines.state")
    def _compute_extra_quantity(self):
        for record in self:
            po_lines_related = self.env["purchase.order.line"].search(
                [
                    ("related_requisition_line_id", "=", record.id),
                    ("order_id.state", "in", ["purchase", "done"]),
                ]
            )

            total_received = sum(po_lines_related.mapped("product_qty"))
            total_received_qty = sum(po_lines_related.mapped("qty_received"))

            record.extra_ordered_quantity = total_received - record.received_qty
            # record.remaining_ordered_quantity = record.product_qty - record.extra_ordered_quantity

    @api.depends("product_qty", "extra_ordered_quantity", "received_qty", "status", "related_po_lines",
                 "related_po_lines.order_id.picking_ids.state", "related_po_lines.qty_received")
    def _compute_remaining_ordered_quantity(self):
        for record in self:
            po_lines_related_received = self.env["purchase.order.line"].search(
                [
                    ("related_requisition_line_id", "=", record.id),
                    ("order_id.state", "in", ["purchase", "done"]),
                    ("qty_received", ">", 0),
                ]
            )

            po_lines_related = self.env["purchase.order.line"].search(
                [
                    ("related_requisition_line_id", "=", record.id),
                    ("order_id.state", "in", ["purchase", "done"]),
                ]
            )

            total_shipped = sum(po_lines_related.mapped("product_qty"))
            total_received_qty = sum(po_lines_related_received.mapped("qty_received"))
            record.remaining_ordered_quantity = record.product_qty - record.extra_ordered_quantity - total_received_qty

    @api.depends("remaining_ordered_quantity", "price_unit")
    def _compute_remaining_price(self):
        for line in self:
            line.remaining_price = line.remaining_ordered_quantity * line.price_unit

    @api.depends("product_id", "requisition_id", "requisition_id.name")
    def _compute_name(self):
        for requisition in self:
            requisition.name = (
                    requisition.product_id.name + " / " + requisition.requisition_id.name
            )
            requisition.display_name = requisition.name

    @api.depends("extra_ordered_quantity", "price_unit")
    def _compute_shipped_value(self):
        for line in self:
            line.shipped_value = line.extra_ordered_quantity * line.price_unit

    def action_create_rfq(self):
        selected_lines = self.env["purchase.requisition.line"].browse(
            self._context.get("active_ids", [])
        )

        vendors = selected_lines.mapped("vendor_id")
        if len(vendors) > 1:
            raise UserError("You cannot create an RFQ with different Vendors.")

        vendor = vendors[0]
        purchase_order = (
            self.env["purchase.order"]
            .sudo()
            .create(
                {
                    "partner_id": vendor.id,
                    # 'requisition_id': requisition.id,
                    "order_line": [],
                }
            )
        )
        purchase_order.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "related_requisition_line_id": line.id,
                            "product_id": line.product_id.id,
                        },
                    )
                    for line in selected_lines
                ],
            }
        )

        return {
            "name": "Request for Quotation",
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "view_mode": "form",
            "res_id": purchase_order.id if purchase_order else False,
            "target": "current",
        }


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    total_quantities = fields.Float(
        compute="compute_total_quants", digits=(16, 0), store=True, precompute=True
    )

    total_amount = fields.Float(
        compute="compute_total_quants", store=True, precompute=True
    )

    # remaining_ordered_quantity = fields.Float(
    #     compute="_compute_remaining_quantity",
    #     digits=(16, 0),
    #     store=True,
    #     precompute=True,
    # )

    # state = fields.Selection(store=True)

    # total_amount = fields.Float(compute='compute_total_quants', digits=(16, 0), store=True,)

    total_original_qty = fields.Float(
        string="Requested Qty",
        compute="_compute_total_original_qty",
        digits=(16, 0),
        precompute=True,
        store=True,
    )
    total_original_u_price = fields.Float(
        string="Requested Price",
        compute="_compute_requested_total",
        store=True,
        precompute=True,
    )

    total_confirmed_price = fields.Float(
        string="Confirmed Price",
        compute="_compute_confirmed_price",
        store=True,
        precompute=True,
    )
    total_confirmed_qty = fields.Float(
        string="Confirmed QTY",
        compute="_compute_confirmed_qty",
        digits=(16, 0),
        precompute=True,
        store=True,
    )
    total_remaining_confirmed_qty = fields.Float(
        string="Remaining Confirmed QTY",
        compute="_compute_remaining_confirmed_qty",
        digits=(16, 0),
        precompute=True,
        store=True,
    )
    total_shipped_qty = fields.Float(
        string="Shipped QTY",
        compute="_compute_total_shipped_qty",
        digits=(16, 0),
        precompute=True,
        store=True,
    )
    received_qty = fields.Float(
        string="Received QTY",
        compute="_compute_received_qty",
        digits=(16, 0),
        precompute=True,
        store=True,
    )

    requested_total = fields.Float(
        string="Requested Total",
        compute="_compute_requested_total",
        store=True,
        precompute=True,
    )
    confirmed_total = fields.Float(
        string="Confirmed Total",
        compute="_compute_total",
        store=True,
        precompute=True,
    )
    total_remaining_price = fields.Float(
        string="Remaining Ordered Price",
        compute="_compute_total_remaining_price",
        store=True,
        precompute=True,
    )

    @api.depends("line_ids", "line_ids.remaining_price", "state")
    def _compute_total_remaining_price(self):
        for requisition in self:
            requisition.total_remaining_price = sum(
                line.remaining_price for line in requisition.line_ids
            )

    @api.depends(
        "line_ids", "line_ids.original_qty", "line_ids.original_u_price", "state"
    )
    def _compute_requested_total(self):
        for requisition in self:
            requisition.requested_total = sum(
                line.original_qty * line.original_u_price
                for line in requisition.line_ids
            )
            requisition.total_original_u_price = requisition.requested_total

    @api.depends("line_ids", "line_ids.price_unit", "line_ids.product_qty", "state")
    def _compute_confirmed_price(self):
        for requisition in self:
            requisition.total_confirmed_price = sum(
                line.price_unit * line.product_qty for line in requisition.line_ids
            )

    @api.depends("line_ids", "line_ids.product_qty", "state")
    def _compute_confirmed_qty(self):
        for requisition in self:
            requisition.total_confirmed_qty = sum(
                line.product_qty for line in requisition.line_ids
            )

    @api.depends("line_ids", "line_ids.remaining_ordered_quantity", "state")
    def _compute_remaining_confirmed_qty(self):
        for requisition in self:
            requisition.total_remaining_confirmed_qty = sum(
                line.remaining_ordered_quantity for line in requisition.line_ids
            )

    @api.depends("line_ids", "line_ids.extra_ordered_quantity", "state")
    def _compute_total_shipped_qty(self):
        for requisition in self:
            requisition.total_shipped_qty = sum(
                line.extra_ordered_quantity for line in requisition.line_ids
            )

    @api.depends("line_ids", "line_ids.received_qty", "state")
    def _compute_received_qty(self):
        for requisition in self:
            requisition.received_qty = sum(
                line.received_qty for line in requisition.line_ids
            )

    @api.depends("line_ids", "line_ids.product_qty", "line_ids.price_unit", "state")
    def _compute_total(self):
        for requisition in self:
            requisition.confirmed_total = sum(
                line.product_qty * line.price_unit for line in requisition.line_ids
            )

    @api.depends("line_ids", "line_ids.original_qty", "state")
    def _compute_total_original_qty(self):
        for requisition in self:
            requisition.total_original_qty = sum(
                line.original_qty for line in requisition.line_ids
            )

    def action_in_progress(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(
                _(
                    "You cannot confirm agreement '%s' because there is no product line.",
                    self.name,
                )
            )

        if self.type_id.quantity_copy == "none" and self.vendor_id:
            for requisition_line in self.line_ids:
                if requisition_line.price_unit < 0.0:
                    raise UserError(
                        _("You cannot confirm the blanket order with a negative price.")
                    )

                if requisition_line.product_qty < 0.0:
                    raise UserError(
                        _(
                            "You cannot confirm the blanket order with a negative quantity."
                        )
                    )

                requisition_line.create_supplier_info()

            self.write({"state": "ongoing"})
        else:
            self.write({"state": "in_progress"})

        if self.name == "New":
            self.name = (
                self.env["ir.sequence"]
                .with_company(self.company_id)
                .next_by_code("purchase.requisition.blanket.order")
            )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    remaining_ordered_quantity = fields.Float(
        related="related_requisition_line_id.remaining_ordered_quantity",
        string="Remaining Ordered QTY",
        store=True,
        digits=(16, 0),
    )

    product_readonly = fields.Boolean("", compute="_compute_product_readonly")

    @api.depends("related_requisition_line_id")
    def _compute_product_readonly(self):
        for line in self:
            if line.related_requisition_line_id:
                line.product_readonly = True
            else:
                line.product_readonly = False

    @api.depends("product_packaging_qty", "related_requisition_line_id")
    def _compute_product_qty(self):
        super()._compute_product_qty()
        for line in self:
            if line.related_requisition_line_id:
                requisition_line = line.related_requisition_line_id
                line.product_qty = requisition_line.product_qty

    def _suggest_quantity(self):
        if self.related_requisition_line_id:
            self.product_qty = self.related_requisition_line_id.product_qty
        else:
            super()._suggest_quantity()

    @api.depends(
        "product_qty", "product_uom_id", "company_id", "related_requisition_line_id"
    )
    def _compute_price_unit_and_date_planned_and_name(self):
        super()._compute_price_unit_and_date_planned_and_name()
        for line in self:
            if line.related_requisition_line_id:
                requisition_line = line.related_requisition_line_id
                line.price_unit = requisition_line.price_unit
                _logger.info(f"\n\n\n\n\n\n price_unit {line.price_unit}")

    @api.onchange("related_requisition_line_id")
    def _onchange_requisition_line_id(self):
        for line in self:
            _logger.info(f"\n\n\n\\\n\n\n\n\n\n\n testtt")
            if line.related_requisition_line_id:
                _logger.info(f"\n\n\n\\\n\n\n\n\n\n\n testtt")
                line.product_id = line.related_requisition_line_id.product_id
                # line.product_qty = line.related_requisition_line_id.product_qty
                # line.price_unit = line.related_requisition_line_id.price_unit
                # _logger.info(f"\n\n\n\\\n\n\n\n\n\n\n testt {line.product_qty} {line.related_requisition_line_id.product_qty}")


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    total_quantity = fields.Float(
        compute="_compute_total_quantity",
        store=True,
        digits=(16, 0),
    )

    @api.constrains("order_line", "partner_id")
    def _check_vendor_in_requisition_line(self):
        for order in self:
            vendor = order.partner_id

            if not vendor:
                continue

            for line in order.order_line:
                if line.related_requisition_line_id:
                    product_vendor = line.related_requisition_line_id.vendor_id
                    if product_vendor and product_vendor != vendor:
                        raise UserError(
                            f"The product has a different vendor ({product_vendor.name}) "
                            f"than the selected requisition vendor ({vendor.name})."
                        )

    def button_confirm(self):
        for order in self:
            for line in order.order_line:
                if line.related_requisition_line_id:
                    if line.product_qty > line.remaining_ordered_quantity:
                        raise UserError(
                            _(
                                "The quantity ordered for product %s exceeds the remaining quantity in the Blanket Order!"
                            )
                            % line.product_id.display_name
                        )
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            for line in order.order_line:
                if line.related_requisition_line_id:
                    line.related_requisition_line_id._get_related_po_lines()

        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for picking in self:
            for line in picking.move_ids:
                if line.purchase_line_id:
                    if line.purchase_line_id.related_requisition_line_id:
                        _logger.info("\n\n\n\n\n\n\\n\n hereeeee")
                        line.purchase_line_id.related_requisition_line_id.sudo()._get_related_po_lines()
        return res
