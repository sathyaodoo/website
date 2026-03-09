# from odoo import api, fields, models, _
# from odoo.exceptions import ValidationError, AccessError, UserError
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class ProductBrand(models.Model):
#     _inherit = 'product.brand'
#
#     analytic_account_id = fields.Many2one(
#         'account.analytic.account',
#         string="Analytical Distribution (Stock)",
#         company_dependent=True,
#         required=True
#     )
#     brand_analytic_account_id = fields.Many2one(
#         'account.analytic.account',
#         string="Analytical Distribution (Brand)",
#         company_dependent=True,
#         required=True
#     )
#
#     @api.model
#     def create(self, vals):
#         brand = super(ProductBrand, self).create(vals)
#         # Transfer the customization of automated stock valuation from Forfait to Marwan SARL
#         forfait_company_id = self.env['res.company'].sudo().browse(1)
#         target_company_id = forfait_company_id.id
#         target_company_name = forfait_company_id.name
#         brands = self.sudo().search([('id', '=', self.id)])  # Get all product brands
#         _logger.info(f"\n\n\n\n *********all product brands **create*{brands}********")
#         if not brands and self.env.company != forfait_company_id:
#             raise UserError(
#                 f'You must login in company {forfait_company_id.name} and create this brand from it.')
#         for brand in brands:
#             brand.check_analytic_account_for_company(target_company_id, target_company_name)
#         return brand
#
#     def write(self, vals):
#         result = super(ProductBrand, self).write(vals)
#         # Transfer the customization of automated stock valuation from Forfait to Marwan SARL
#         forfait_company_id = self.env['res.company'].sudo().browse(1)
#         target_company_id = forfait_company_id.id
#         target_company_name = forfait_company_id.name
#         brands = self.sudo().search([(('id', '=', self.id))])  # Get all product brands
#         _logger.info(f"\n\n\n\n *********all product brands **write*{brands}********")
#         for brand in brands:
#             brand.check_analytic_account_for_company(target_company_id, target_company_name)
#         return result
#
#     def check_analytic_account_for_company(self, target_company_id, target_company_name):
#         """Check if the analytic_account_id is set for the specified company."""
#         for record in self:
#             # Fetch the field value for the target company
#             record_in_target_company = record.with_company(target_company_id)
#             _logger.info(
#                 f"\n\n\n\n *********record_in_target_company.analytic_account_id ***{record_in_target_company, record_in_target_company.analytic_account_id}********")
#             if not record_in_target_company.analytic_account_id:
#                 raise UserError(
#                     f"The Stock Analytic Distribution is not set for the product brand '{record.name}' "
#                     f"for the company {target_company_name}."
#                 )
#             if not record_in_target_company.brand_analytic_account_id:
#                 raise UserError(
#                     f"The Brand Analytic Distribution is not set for the product brand '{record.name}' "
#                     f"for the company {target_company_name}."
#                 )
#
#     @api.constrains('analytic_account_id')
#     def check_stock_analytic_company(self):
#         for brand in self:
#             if brand.analytic_account_id:
#                 login_company = self.env.company
#                 analytic_brand_company = brand.analytic_account_id.company_id
#                 analytic_brand_plan = brand.analytic_account_id.plan_id
#                 if analytic_brand_company:
#                     if analytic_brand_company != login_company and analytic_brand_company != login_company.parent_id:
#                         raise UserError(
#                             f'The company of stock analytic distribution must be same as the login company {login_company.name}.')
#
#                 if analytic_brand_plan.id != 3:
#                     raise UserError(
#                         f'The plan of stock analytic distribution must be Stock Valuation.')
#
#     @api.constrains('brand_analytic_account_id')
#     def check_brand_analytic_company(self):
#         for brand in self:
#             if brand.brand_analytic_account_id:
#                 login_company = self.env.company
#                 analytic_brand_company = brand.brand_analytic_account_id.company_id
#                 analytic_brand_plan = brand.brand_analytic_account_id.plan_id
#                 if analytic_brand_company:
#                     if analytic_brand_company != login_company and analytic_brand_company != login_company.parent_id:
#                         raise UserError(
#                             f'The company of brand analytic distribution must be same as the login company {login_company.name} .')
#
#                 if analytic_brand_plan.id != 2:
#                     raise UserError(
#                         f'The plan of brand analytic distribution must be Brands.')
