from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_log = logging.getLogger(__name__)



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    fixed_asset_ok = fields.Boolean('Can be Fixed Asset', default=False)

    @api.onchange('fixed_asset_ok')
    def _onchange_fixed_asset_ok(self):
        for rec in self:
             if rec.fixed_asset_ok == True:
                 if rec.detailed_type != 'product':
                     raise UserError(
                         _('You cannot use this product (%s) as fixed asset, check the field \'Product Type\' it must be Storable.',
                           rec.display_name))
