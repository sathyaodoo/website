# Copyright 2013 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class StockReservation(models.Model):
    """Allow to reserve products.

    The fields mandatory for the creation of a reservation are:

    * product_id
    * product_uom_qty
    * product_uom
    * name

    The following fields are required but have default values that you may
    want to override:

    * company_id
    * location_id
    * location_dest_id

    Optionally, you may be interested to define:

    * date_validity  (once passed, the reservation will be released)
    * note
    """

    _name = "stock.reservation"
    _description = "Stock Reservation"
    _inherit = ['mail.thread']
    _inherits = {"stock.move": "move_id"}

    location_track_id = fields.Many2one(
        'stock.location', 'Source Location',
        tracking=True, related="move_id.location_id")

    location_dest_track_id = fields.Many2one(
        'stock.location', 'Destination Location',
        tracking=True, related="move_id.location_dest_id")

    product_track_id = fields.Many2one(
        'product.product', 'Product',
        tracking=True, related="move_id.product_id")

    product_uom_track_qty = fields.Float(
        'Demand',
        tracking=True, related="move_id.product_uom_qty")

    product_track_uom = fields.Many2one(
        'uom.uom', "UoM", tracking=True, related="move_id.product_uom")

    restrict_lot_track_id = fields.Many2one("stock.lot", string="Restrict Lot", tracking=True,)

    track_name = fields.Char('Description', tracking=True,)
    company_track_id = fields.Many2one(
        'res.company', 'Company',
        tracking=True, related="move_id.company_id")
    note = fields.Text(string="Notes", tracking=True)
    move_id = fields.Many2one("stock.move", "Reservation Move", required=True, readonly=True, ondelete="cascade",
                              index=True)
    date_validity = fields.Date("Validity Date", default=datetime.today() + timedelta(days=30), tracking=True, )
    reservation_group_id = fields.Many2one('stock.reservation.group', string='Stock Reservation Group',
                                           default=lambda self: self.env.user.reservation_group_id, required=True,
                                           tracking=True, )
    available_quant = fields.Float("Available Quantity", tracking=True, compute="_compute_available_quantity")
    categ_id = fields.Many2one(related='product_id.categ_id', store=True)

    # to fix
    # @api.depends('location_id', 'product_id', 'restrict_lot_id')
    def _compute_available_quantity(self):
        """
        In order for the compute to work properly on v-17, make sure to create an automation rule:
            Model: Stock Reservation
            Trigger: On save
            When updating: Demand
            Action: Execute Code:
                    if record:
                        record._compute_available_quantity()
        """
        for rec in self:
            rec.available_quant = 0
            if rec.location_id:
                if rec.restrict_lot_id and rec.categ_id.id != 24:
                    quantity = self.env["stock.quant"].sudo().search([
                        ("location_id", "=", rec.location_id.id),
                        ("product_id", "=", rec.product_id.id),
                        ("lot_id", "=", rec.restrict_lot_id.id)
                    ])
                    rec.available_quant = sum(quantity.mapped("available_quantity"))
                elif rec.categ_id.id == 24:
                    quantity = self.env["stock.quant"].sudo().search([
                        ("location_id", "=", rec.location_id.id),
                        ("product_id", "=", rec.product_id.id),
                    ])
                    rec.available_quant = sum(quantity.mapped("available_quantity"))

    @api.model
    def default_get(self, fields_list):
        """Fix default values

        - Ensure default value of computed field `product_qty` is not set
          as it would raise an error
        - Compute default `location_id` based on default `picking_type_id`.
          Note: `default_picking_type_id` may be present in context,
          so code that looks for default `location_id` is implemented here,
          because it relies on already calculated default
          `picking_type_id`.
        """
        # if there is 'location_id' field requested, ensure that
        # picking_type_id is also requested, because it is required
        # to compute location_id
        if "location_id" in fields_list and "picking_type_id" not in fields_list:
            fields_list = fields_list + ["picking_type_id"]

        res = super().default_get(fields_list)

        if "product_qty" in res:
            del res["product_qty"]

        # At this point picking_type_id and location_id
        # should be computed in default way:
        #     1. look up context
        #     2. look up ir_values
        #     3. look up property fields
        #     4. look up field.default
        #     5. delegate to parent model
        #
        # If picking_type_id is present and location_id is not, try to find
        # default value for location_id
        if not res.get("picking_type_id", None):
            res["picking_type_id"] = self._default_picking_type_id()
        picking_type_id = res.get("picking_type_id")

        res["location_id"] = self.env["stock.location"].search([('id', '=', 8)]).id
        if picking_type_id and not res.get("location_id", False):
            picking = self.env["stock.picking"].new({"picking_type_id": picking_type_id})
            picking._onchange_picking_type()
            res["location_id"] = picking.location_id.id
        if "location_dest_id" in fields_list:
            res["location_dest_id"] = self._default_location_dest_id()
        if "product_uom_qty" in fields_list:
            res["product_uom_qty"] = 1.0
        return res

    @api.model
    def get_location_from_ref(self, ref):
        """Get a location from a xmlid if allowed
        :param ref: tuple (module, xmlid)
        """
        try:
            location = self.env.ref(ref, raise_if_not_found=True)
            location.check_access_rule("read")
            location_id = location.id
        except (UserError, ValueError):
            location_id = False
        return location_id

    @api.model
    def _default_picking_type_id(self):
        ref = "stock.picking_type_out"
        return self.env.ref(ref, raise_if_not_found=False).id

    @api.model
    def _default_location_dest_id(self):
        ref = "stock_reserve.stock_location_reservation"
        return self.get_location_from_ref(ref)

    def reserve(self):
        """Confirm reservations

        The reservation is done using the default UOM of the product.
        A date until which the product is reserved can be specified.
        """
        for rec in self:
            if rec.product_uom_qty > rec.available_quant and rec.state != 'partially_available':
                raise ValidationError(
                    _(f'The reservation is not fully available. Requesting: {rec.product_uom_qty} {rec.product_uom.name} / Maximum Available: {rec.available_quant} {rec.product_uom.name}'))

        user_reservation_group_id = self.env.user.reservation_group_id
        if user_reservation_group_id and not self.env.user.has_group('stock_reserve.erpc_stock_reservation_manager'):
            for rec in self:
                if rec.reservation_group_id != user_reservation_group_id:
                    raise ValidationError(
                        "You are not allowed to confirm this reservation as it does not belong to your reservation group.")

        self.write({"date": fields.Datetime.now()})
        # Don't call _action_confirm() method to prevent assign picking
        self.mapped("move_id").write({"state": "confirmed"})
        self.mapped("move_id")._action_assign()
        return True

    def release_reserve(self):
        """
        Release moves from reservation and log the action in the chatter
        """
        user_reservation_group_id = self.env.user.reservation_group_id
        if user_reservation_group_id and not self.env.user.has_group('stock_reserve.erpc_stock_reservation_manager'):
            for rec in self:
                if rec.reservation_group_id != user_reservation_group_id:
                    raise ValidationError(
                        "You are not allowed to release this reservation as it does not belong to your reservation group.")

        # Cancel the moves
        moves = self.mapped("move_id")
        moves._action_cancel()

        # Post a message in the chatter
        for rec in self:
            rec.message_post(
                body=f"Reservation released by {self.env.user.name}.",
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )

        return True

    def _get_state_domain_release_reserve(self, mode):
        if mode == "reserve":
            return
        elif mode == "release":
            return "cancel"

    @api.model
    def release_validity_exceeded(self, ids=None):
        """Release all the reservation having an exceeded validity date"""
        domain = [
            ("date_validity", "<", fields.date.today()),
            ("state", "!=", "cancel"),
        ]
        if ids:
            domain.append(("id", "in", ids))
        self.env["stock.reservation"].search(domain).release_reserve()
        return True
        
    def copy(self, default=None):
        raise ValidationError(_("You cannot duplicate a stock reservation record."))
        
    def unlink(self):
        """Prevent unlinking and raise an error instead"""
        raise ValidationError(_("You cannot delete a stock reservation. Please release the reservation instead."))

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """set product_uom and name from product onchange"""
        # save value before reading of self.move_id as this last one erase
        # product_id value
        self.move_id.product_id = self.product_id
        self.move_id._onchange_product_id()
        self.name = self.move_id.name
        self.product_uom = self.move_id.product_uom

    @api.onchange("product_uom_qty")
    def _onchange_quantity(self):
        """On change of product quantity avoid negative quantities"""
        if not self.product_id or self.product_uom_qty <= 0.0:
            self.product_uom_qty = 0.0

    @api.onchange("restrict_lot_id")
    def _onchange_restrict_lot_id(self):
        self.lot_ids = [(6, 0, [self.restrict_lot_id])]

    def open_move(self):
        self.ensure_one()
        action_dict = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.stock_move_action"
        )
        action_dict["name"] = _("Reservation Move")
        # open directly in the form view
        view_id = self.env.ref("stock.view_move_form").id
        action_dict.update(views=[(view_id, "form")], res_id=self.move_id.id)
        return action_dict

    def write(self, vals):
        if "product_uom_qty" in vals or "product_uom" in vals:
            user_reservation_group_id = self.env.user.reservation_group_id
            if user_reservation_group_id and not self.env.user.has_group(
                    'stock_reserve.erpc_stock_reservation_manager'):
                for rec in self:
                    if rec.reservation_group_id != user_reservation_group_id:
                        raise ValidationError(
                            "You are not allowed to modify quantities of this reservation as it does not belong to your reservation group.")

        org_state, org_product_uom_qty, org_available_quant = self._origin.state, self._origin.product_uom_qty, self._origin.available_quant

        res = super().write(vals)
        if "product_uom_qty" in vals:
            rounding = self.product_uom.rounding
            if (self.state in ["confirmed", "waiting", "partially_available"]
                    and float_compare(self.product_id.virtual_available, 0, precision_rounding=rounding) >= 0):
                self.reserve()

            for rec in self:
                origin_available_qty = org_product_uom_qty + org_available_quant

                if rec.product_uom_qty > origin_available_qty:
                    raise ValidationError(
                        _(f'The reservation is not fully available. Requesting: {rec.product_uom_qty} {rec.product_uom.name} / Maximum Available: {origin_available_qty} {rec.product_uom.name}'))
        return res

    def _get_reservations_to_assign_domain(self):
        return [
            ("state", "in", ["confirmed", "waiting", "partially_available"]),
            "|",
            ("date_validity", ">=", fields.date.today()),
            ("date_validity", "=", False),
        ]

    @api.model
    def assign_waiting_confirmed_reserve_moves(self):
        reservations_to_assign = self.search(self._get_reservations_to_assign_domain())
        for reservation in reservations_to_assign:
            reservation.reserve()
        return True
