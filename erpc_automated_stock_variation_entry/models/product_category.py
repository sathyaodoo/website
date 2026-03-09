from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string='Analytical Distribution (Stock)',
                                          company_dependent=True)
                                          # required=True)

    @api.model
    def create(self, vals):
        category = super(ProductCategory, self).create(vals)

        analytic_distribution_dict = {}
        analytic_distribution_dict[category.analytic_account_id.id] = 100

        for prefix in [6, 7]:
            self.env['account.analytic.distribution.model'].create({
                'account_prefix': prefix,
                'product_categ_id': category.id,
                'analytic_distribution': analytic_distribution_dict,
            })

        return category


