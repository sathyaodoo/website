from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SalesNote(models.Model):
    _name = 'sales.note'

    title = fields.Char(string='Title')
    description = fields.Text(string='Description')
    attachment = fields.Binary(string='Attachment')
    attachment_filename = fields.Char(string='Attachment Filename')
    active = fields.Boolean(string="Active", default=True)

    has_attachment = fields.Boolean(
        string="Has Attachment",
        compute="_compute_has_attachment",
        store=True
    )

    @api.depends("attachment")
    def _compute_has_attachment(self):
        for rec in self:
            rec.has_attachment = bool(rec.attachment)

    def archive_note(self):
        return self.write({'active': False})

    def unarchive_note(self):
        return self.write({'active': True})

    def download_attachment(self):
        """Works exactly like the binary field download button"""
        self.ensure_one()
        if not self.attachment:
            raise ValidationError(_("No attachment found!"))

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content?model=sales.note&id=%s&field=attachment&filename_field=attachment_filename&download=true' % self.id,
            'target': 'self',
        }
