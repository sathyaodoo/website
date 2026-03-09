from odoo import fields, models, api


class VendorBillsInherit(models.Model):
    _inherit = 'account.move'

    customer_id = fields.Many2one('res.partner', string='To Which Customer')
    to_partner_id = fields.Many2one('res.partner', string="TO", domain="[('child_ids', '!=', False)]")
    can_auto_send = fields.Boolean(name="Can Send Automatically", default=False)

    @api.model
    def write(self, vals):
        for rec in self:
            if not rec.can_auto_send:
                vals['can_auto_send'] = True

        super(VendorBillsInherit, self).write(vals)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    to_partner_id = fields.Many2one('res.partner',string="TO", related="move_id.to_partner_id", store=True)
