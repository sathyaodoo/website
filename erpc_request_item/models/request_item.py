from odoo import models, fields, api
from odoo.exceptions import UserError


class RequestItem(models.Model):
    _name = 'request.item'
    _description = "Employee Request Item"

    name = fields.Char(string="Name", default="/")
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True, default=lambda self: self.env.user.company_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', copy=False)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)
    request_ids = fields.One2many('request.item.line', 'request_id')

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('request.for.item.seq') or '/'
        res = super(RequestItem, self).create(values)
        return res

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def action_submit(self):
        self.write({'state': 'waiting_approval_1'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        self.ensure_one()
        order_lines = []
        for request_line in self.request_ids:
            order_lines.append((0, 0, {
                'product_id': request_line.product_id.id,
                'discount': '100',
                'lot_id': request_line.lot_id.id,
                'product_uom_qty': request_line.product_uom_qty,
                'price_unit': request_line.price_unit * request_line.product_uom_qty
            }))
        sale_order = self.env['sale.order'].create({
            'partner_id': self.employee_id.work_contact_id.id,
            'order_line': order_lines,
        })
        self.write({'state': 'approve', 'sale_order_id': sale_order.id})

    def unlink(self):
        for request in self:
            if request.state not in ('draft', 'cancel'):
                raise UserError('You cannot delete a request which is not in draft or cancelled state')

        return super(RequestItem, self).unlink()
