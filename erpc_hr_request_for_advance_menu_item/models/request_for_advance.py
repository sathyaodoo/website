from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo.tools.float_utils import float_compare

ADVANCE_STATE_SELECTION = [
    ('draft', 'New'),
    ('waiting_approval_1', 'Submitted'),
    ('approve', 'Approved'),
    ('paid', 'Paid'),
    ('partially_closed', 'Partially Closed'),
    ('closed', 'Closed'),
    ('refused', 'Refused'),
]


class HrAdvanceRequest(models.Model):
    _name = 'hr.advance.request'
    _description = 'Request for Advance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_employee_domain(self):
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if employee:
            return [('id', '=', employee.id)]
        return []

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)

    name = fields.Char(string='Reference', default='New', readonly=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        tracking=True,
        default=lambda self: self._default_employee()
    )

    @api.onchange('employee_id')
    def _onchange_employee_domain(self):
        is_advance_requester = self.env.user.has_group(
            'erpc_hr_request_for_advance_menu_item.group_advance_requester'
        )
        if is_advance_requester:
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            return {
                'domain': {
                    'employee_id': [('id', '=', employee.id)] if employee else []
                }
            }
        else:
            return {
                'domain': {
                    'employee_id': []
                }
            }

    advancement_type = fields.Selection([
        ('short', 'Short Advance'),
        ('long', 'Long Advance')
    ], string='Advancement Type', required=True, tracking=True)
    amount = fields.Float(string='Amount', required=True, tracking=True)
    number_of_instalments = fields.Integer(string='Number of Instalments', default=1)

    payment_start_date = fields.Date(
        string='Payment Start Date',
        required=True,
        default=lambda self: date.today().replace(day=25),
    )

    payment_start_date_readonly = fields.Boolean(
        string='Payment Start Date Readonly',
        compute='_compute_payment_start_date_readonly'
    )

    advance_lines = fields.One2many('hr.advance.line', 'advance_id', string='Installments')

    total_amount = fields.Float(string='Total Amount', compute='_compute_totals', store=True)
    total_paid_amount = fields.Float(string='Total Paid Amount', compute='_compute_totals', store=True)
    balance_amount = fields.Float(string='Balance Amount', compute='_compute_totals', store=True)

    currency_id = fields.Many2one(related='company_id.currency_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    reason = fields.Text("Reason of Refusal")
    request_reason = fields.Text(string="Reason", required=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('waiting_approval_1', 'Submitted'),
        ('approve', 'Approved'),
        ('paid', 'Paid'),
        ('partially_closed', 'Partially Closed'),
        ('closed', 'Closed'),
        ('refused', 'Refused'),
    ], string='Status', default='draft', copy=False, tracking=True)

    can_edit_line = fields.Boolean(string='Can Edit', compute='_compute_can_edit_line')
    amount_mismatch = fields.Boolean(
        string='Amounts Mismatch',
        compute='_compute_amount_mismatch',
        store=False,
    )
    advance_state = fields.Selection(
        selection=ADVANCE_STATE_SELECTION,
        string="Payment Status",
        compute='_compute_advance_state', store=True, readonly=True,
        copy=False,
    )

    def _compute_payment_start_date_readonly(self):
        is_hr_advance = self.env.user.has_group('erpc_hr_request_for_advance_menu_item.group_advance_hr')
        is_manager_advance = self.env.user.has_group('erpc_hr_request_for_advance_menu_item.group_advance_manager')
        for record in self:
            record.payment_start_date_readonly = not (is_hr_advance or is_manager_advance)

    @api.depends('state', 'advance_lines.paid')
    def _compute_can_edit_line(self):
        for rec in self:
            if rec.state == 'closed':
                rec.can_edit_line = False
            elif rec.state == 'partially_closed':
                unpaid_lines = rec.advance_lines.filtered(lambda l: not l.paid)
                rec.can_edit_line = bool(unpaid_lines)
            else:
                rec.can_edit_line = True

    is_balanced = fields.Boolean(string='Is Balanced', compute='_compute_is_balanced', store=True)

    is_advance_requester = fields.Boolean(string="Is Advance Requester", compute="_compute_advance_request")
    is_hr_advance = fields.Boolean(string="Is HR", compute="_compute_advance_request")
    is_manager_advance = fields.Boolean(string="Is Manager", compute="_compute_advance_request")

    @api.onchange('payment_start_date')
    def _onchange_payment_start_date(self):
        if not (self.is_hr_advance or self.is_manager_advance):
            if self.payment_start_date != date.today().replace(day=25):
                raise UserError(_("Only HR or Manager can update the Payment Start Date."))
                self.payment_start_date = date.today().replace(day=25)

    @api.onchange('advancement_type')
    def _compute_advance_request(self):
        is_advance_requester_group = self.env.user.has_group(
            'erpc_hr_request_for_advance_menu_item.group_advance_requester')
        is_hr_advance_group = self.env.user.has_group('erpc_hr_request_for_advance_menu_item.group_advance_hr')
        is_manager_advance_group = self.env.user.has_group(
            'erpc_hr_request_for_advance_menu_item.group_advance_manager')

        for record in self:
            record.is_advance_requester = is_advance_requester_group
            record.is_hr_advance = is_hr_advance_group
            record.is_manager_advance = is_manager_advance_group

    @api.onchange('advancement_type')
    def _onchange_advancement_type(self):
        if self.advancement_type == 'short':
            self.number_of_instalments = 1
        elif self.advancement_type == 'long':
            self.number_of_instalments = 0

    @api.depends('advance_lines.paid', 'advance_lines.amount')
    def _compute_totals(self):
        for rec in self:
            rec.total_amount = sum(line.amount for line in rec.advance_lines)
            rec.total_paid_amount = sum(line.amount for line in rec.advance_lines if line.paid)
            rec.balance_amount = rec.total_amount - rec.total_paid_amount
            # if rec.total_amount > 0:
            #     rec.amount = rec.total_amount

            if rec.state in ['approve', 'paid', 'partially_closed']:
                if rec.balance_amount <= 0 and rec.total_amount > 0:
                    rec.state = 'closed'
                elif 0 < rec.balance_amount < rec.total_amount:
                    rec.state = 'partially_closed'
                elif rec.balance_amount == rec.total_amount and rec.state == 'approve':
                    rec.state = 'approve'

    @api.depends('total_paid_amount', 'total_amount')
    def _compute_is_balanced(self):
        for rec in self:
            rec.is_balanced = rec.total_amount == rec.total_paid_amount

    @api.depends('state')
    def _compute_advance_state(self):
        for adv in self:
            adv.advance_state = adv.state

    def action_submit(self):
        for rec in self:
            if not rec.advance_lines:
                raise UserError(_("You must compute installments first."))
            if rec.total_amount != rec.amount:
                raise ValidationError(_("For this request for advance Total Amount is different from Amount."))

            rec.write({'state': 'waiting_approval_1'})
            manager_group = self.env.ref('erpc_hr_request_for_advance_menu_item.group_advance_hr')
            managers = manager_group.sudo().all_user_ids - self.env.user

            subject = _("Request for Advance Submitted")

            # Send notification to HR
            for manager in managers:
                body_html = _(
                    f"<p>Dear {manager.name},</p>"
                    f"<p>The following request for advance <strong>{rec.name}</strong> has been submitted.</p>"
                    f"<p>Kindly review and approve.</p>"
                )
                activity_values = {
                    'res_model_id': self.env['ir.model']._get_id('hr.advance.request'),
                    'res_id': rec.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_email').id,
                    'summary': subject,
                    'note': body_html,
                    'user_id': manager.id,
                    'date_deadline': fields.Date.context_today(self),
                }
                self.env['mail.activity'].sudo().create(activity_values)

    def action_approve(self):
        short_ceiling = self.company_id.ceiling_limit_for_short_advance
        long_ceiling = self.company_id.ceiling_limit_for_long_advance

        for rec in self:
            is_hr = self.env.user.has_group('erpc_hr_request_for_advance_menu_item.group_advance_hr')
            is_manager = self.env.user.has_group('erpc_hr_request_for_advance_menu_item.group_advance_manager')
            if rec.total_amount != rec.amount:
                raise ValidationError(_("For this request for advance Total Amount is different from Amount."))

            if rec.advancement_type == 'short':
                if rec.amount > short_ceiling:
                    if not is_manager:
                        raise UserError(_("Only the CFO can approve short advance requests above the ceiling limit."))
                else:
                    if not (is_hr or is_manager):
                        raise UserError(
                            _("Only HR or Manager can approve short advance requests under the ceiling limit."))

            elif rec.advancement_type == 'long':
                if rec.amount > long_ceiling:
                    if not is_manager:
                        raise UserError(_("Only the CFO can approve long advance requests above the ceiling limit."))
                else:
                    if not (is_hr or is_manager):
                        raise UserError(
                            _("Only HR or Manager can approve long advance requests under the ceiling limit."))

        self.write({'state': 'approve'})

    def action_refuse(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reason Of Refusal',
            'res_model': 'reason.of.refusal',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_compute_installment(self):
        self.ensure_one()

        if not self.payment_start_date:
            raise UserError(_("Please set the Payment Start Date first."))

        if self.state == 'partially_closed':
            paid_lines = self.advance_lines.filtered(lambda line: line.paid)
            total_paid = sum(paid_lines.mapped('amount'))

            self.advance_lines.filtered(lambda line: not line.paid).unlink()

            remaining_amount = self.amount - total_paid

            if remaining_amount < 0:
                raise UserError(_("Paid amount exceeds total advance amount."))

            if self.advancement_type == 'short':
                if remaining_amount > 0:
                    self.env['hr.advance.line'].create({
                        'advance_id': self.id,
                        'payment_date': self.payment_start_date,
                        'amount': remaining_amount,
                        'paid': False,
                    })
            else:
                if self.number_of_instalments <= 0:
                    raise UserError(_("Number of installments must be greater than 0 for long advances."))

                amount_per_installment = remaining_amount / self.number_of_instalments
                current_date = self.payment_start_date

                for i in range(self.number_of_instalments):
                    self.env['hr.advance.line'].create({
                        'advance_id': self.id,
                        'payment_date': current_date,
                        'amount': amount_per_installment,
                        'paid': False,
                    })
                    current_date += relativedelta(months=1)

        else:
            self.advance_lines.unlink()

            if self.advancement_type == 'short':
                self.env['hr.advance.line'].create({
                    'advance_id': self.id,
                    'payment_date': self.payment_start_date,
                    'amount': self.amount,
                    'paid': False,
                })
            else:
                if self.number_of_instalments <= 0:
                    raise UserError(_("Number of installments must be greater than 0 for long advances."))

                amount_per_installment = self.amount / self.number_of_instalments
                current_date = self.payment_start_date

                for i in range(self.number_of_instalments):
                    self.env['hr.advance.line'].create({
                        'advance_id': self.id,
                        'payment_date': current_date,
                        'amount': amount_per_installment,
                        'paid': False,
                    })
                    current_date += relativedelta(months=1)

        return True

    @api.model
    def create(self, vals):
        if isinstance(vals, list):
            for val in vals:
                if val.get('name', 'New') == 'New':
                    val['name'] = self.env['ir.sequence'].next_by_code('hr.advance.request') or 'New'
            return super().create(vals)

        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.advance.request') or 'New'
        return super().create(vals)

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("You cannot delete a request that isn't New.")
        return super(HrAdvanceRequest, self).unlink()

    @api.depends('amount', 'total_amount')
    def _compute_amount_mismatch(self):
        for rec in self:
            rec.amount_mismatch = float_compare(rec.total_amount, rec.amount, precision_digits=2) != 0

class HrAdvanceLine(models.Model):
    _name = 'hr.advance.line'
    _description = 'Advance Installment Line'

    advance_id = fields.Many2one('hr.advance.request', string='Advance')
    payment_date = fields.Date(string='Payment Date', required=True)
    amount = fields.Float(string='Amount', required=True)
    paid = fields.Boolean(string='Paid', compute='_compute_paid', store=True)
    payslip_name = fields.Many2one('hr.payslip', string='Payslip')
    payslip_reference = fields.Char(related='payslip_name.employee_reference', store=True, readonly=True, string='Reference')
    batch_name = fields.Many2one('hr.payslip.run', string='Batch')

    @api.depends('payslip_name.state')
    def _compute_paid(self):
        for line in self:
            line.paid = line.payslip_name and line.payslip_name.state in ('done', 'paid')