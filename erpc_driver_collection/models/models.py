from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
import logging
from datetime import datetime, date

_logger = logging.getLogger(__name__)


class ProductCollection(models.Model):
    _name = 'product.driver'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    can_only_see_all_cash = fields.Boolean(
        string="Can Only See All Cash",
        compute="_compute_can_only_see_all_cash",
        store=False
    )

    @api.depends_context('uid')
    def _compute_can_only_see_all_cash(self):
        """Compute whether the current user has the group 'group_see_only_all_cash'"""
        for rec in self:
            rec.can_only_see_all_cash = self.env.user.has_group('erpc_driver_collection.group_see_only_all_cash')

    name = fields.Char()

    parent_company_id = fields.Many2one('res.partner', tracking=True, change_default=True, index=True,
                                        domain="[('is_driver', '=', False), ('type', '!=', 'private')]")

    partner_id = fields.Many2one('res.partner', tracking=True)
    parent_before = fields.Boolean(string="parent before")

    @api.onchange("parent_company_id")
    def compute_parent_before(self):
        if self.parent_company_id and not self.partner_id:
            self.parent_before = True
        else:
            self.parent_before = False

    usd_currency = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.USD'))
    lbp_currency = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.LBP'))

    price_usd = fields.Monetary('USD', tracking=True, currency_field='usd_currency')
    price_lbp = fields.Monetary('LBP', tracking=True, currency_field='lbp_currency')

    due_date = fields.Datetime(default=fields.Datetime.now, string='Date')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], default="draft", string='Status', tracking=True)

    receipt_usd = fields.Many2one('account.payment', string='USD Receipt', tracking=True, copy=False)
    receipt_lbp = fields.Many2one('account.payment', string='LBP Receipt', tracking=True, copy=False)

    invoice_number = fields.Char(string='Invoice Number', readonly=True, states={'draft': [('readonly', False)]},
                                 copy=False, tracking=True)

    attachment_ids = fields.One2many(
        'ir.attachment', 'res_id',
        domain=lambda self: [('res_model', '=', self._name)],
        string='Attachments',
        help='Attachments related to this record'
    )
    is_creator_driver = fields.Boolean(compute='_compute_is_creator_driver', store=True, precompute=True)

    @api.depends('create_uid')
    def _compute_is_creator_driver(self):
        for record in self:
            record.is_creator_driver = record.create_uid.has_group('erpc_driver_collection.group_is_created_driver')

    driver_name = fields.Many2one('res.partner', string='Driver name', domain=[('is_driver', '=', True)])

    @api.constrains('state', 'driver_name', 'is_creator_driver')
    def _check_driver_name_required(self):
        for record in self:
            if record.state != 'draft' and record.is_creator_driver and not record.driver_name:
                raise ValidationError(
                    "Driver name is not set, Please select the designated driver collecting!If your name is not listed, kindly contact your Administrator.")

    def unlink(self):
        """Override unlink to restrict delete operations."""
        for record in self:
            if self.env.user.has_group('erpc_driver_collection.group_user_driver'):
                raise UserError(_("You are not allowed to delete records."))

            if self.env.user.has_group('erpc_driver_collection.group_admin_driver'):
                if record.state not in ['draft', 'cancelled']:
                    raise UserError(_("You can only delete records in 'Draft' or 'Cancelled' state."))

        return super(ProductCollection, self).unlink()

    @api.model
    def create(self, vals):
        # Generate reference code
        year = datetime.now().year
        next_number = self.env['ir.sequence'].next_by_code(
            'product.collection')  # Optional: Use a dedicated sequence for numbering
        reference = f"COLL/{year}/{next_number.zfill(4)}"  # Format the reference code

        # Update vals dictionary with generated reference
        vals['name'] = reference

        # Call the original create method
        result = super().create(vals)
        return result

    def button_draft(self):
        self.state = 'draft'

    def button_cancel(self):
        self.state = 'cancelled'

    def button_confirm(self):
        for rec in self:
            if not rec.attachment_ids:
                raise ValidationError(_("Please attach a document before confirming."))
        self.state = 'confirmed'

    def button_paid(self):
        self.state = 'paid'

        payment_env = self.env['account.payment']

        vals = {
            "partner_type": "customer",
            "payment_type": "inbound",
            "partner_id": self.partner_id.id,
            # "parent_company_id": self.parent_company_id.id,
            # "date": self.due_date,
            "collection_id": self.id,
            # "ref": self.name,
        }

        usd_vals = {
            "amount": self.price_usd,
            "currency_id": self.usd_currency.id,
            # "partner_currency": self.usd_currency.id,
            "partner_amount": self.price_usd,
        }

        lbp_vals = {
            "amount": self.price_lbp,
            "currency_id": self.lbp_currency.id,
            # "partner_currency": self.lbp_currency.id,
            "partner_amount": self.lbp_currency._convert(self.price_lbp, self.usd_currency, self.env.company,
                                                         self.due_date),
        }

        usd_vals.update(vals)
        lbp_vals.update(vals)

        if self.price_usd:
            payment_usd = payment_env.create(usd_vals)
            self.receipt_usd = payment_usd.id

        if self.price_lbp:
            payment_lbp = payment_env.create(lbp_vals)
            self.receipt_lbp = payment_lbp.id

        return True

    @api.onchange('partner_id')
    def partner_id_onchange(self):
        if self.partner_id:
            self.parent_company_id = self.partner_id.parent_id


class ProductDriverTags(models.Model):
    _name = 'product.driver.tag'
    _rec_name = 'name'

    name = fields.Char()
    code = fields.Char()


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    collection_id = fields.Many2one('product.driver', string='Collection')
    amount_collected = fields.Monetary(string='Collected Amount', currency_field='currency_id', copy=False,
                                       precompute=True, compute='_compute_amount_collect')

    @api.depends('collection_id.price_usd', 'collection_id.usd_currency', 'collection_id.lbp_currency',
                 'collection_id.price_lbp')
    def _compute_amount_collect(self):
        for rec in self:
            if rec.currency_id == rec.collection_id.usd_currency:
                rec.amount_collected = rec.collection_id.price_usd
            elif rec.currency_id == rec.collection_id.lbp_currency:
                rec.amount_collected = rec.collection_id.price_lbp
            else:
                rec.amount_collected = 0
            _logger.info(f'\n\n\n\n*****amount_collected******{rec.amount_collected}\n\n\n\n.')
