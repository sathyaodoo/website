from odoo import api, fields, models, _
import json
from odoo.exceptions import ValidationError, AccessError, UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.fields import Datetime
import logging

_logger = logging.getLogger(__name__)


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    @api.model
    def _create_stock_variation_entry(self):
        ''' This method is called from a cron job.
        It is used to create stock variation entries automatically for company 1 and its branches.
        '''
        _logger.info(f"\n\n\n\n ********* STARTING STOCK VARIATION ENTRY CREATION ***********")

        try:
            # Get company 1 and all its child companies (branches)
            main_company = self.env['res.company'].sudo().browse(1)
            if not main_company:
                _logger.error("Company with ID=1 not found!")
                return False

            all_companies = self.env['res.company'].sudo().search([
                '|', ('id', '=', 1), ('parent_id', '=', 1)
            ])

            _logger.info(f"Found {len(all_companies)} companies to process: {[c.name for c in all_companies]}")

            if not all_companies:
                _logger.error("No companies found to process!")
                return False

            end_of_day = fields.Datetime.now()
            # end_of_day = datetime(2025, 11, 30, 23, 29, 59)
            _logger.info(f"\n\n\n\n *********_create_stock_variation_entry: end_of_day***********{end_of_day}\n\n\n")
            today_start = Datetime.to_datetime(end_of_day).replace(hour=0, minute=0, second=0)
            today_end = Datetime.to_datetime(end_of_day).replace(hour=23, minute=59, second=59)
            yesterday = end_of_day - timedelta(days=1)
            yesterday_end = Datetime.to_datetime(yesterday).replace(hour=23, minute=59, second=59)

            _logger.info(f"Processing period: Today up to {today_end}, Yesterday up to {yesterday_end}")

            successful_companies = 0
            failed_companies = 0

            for company in all_companies:
                _logger.info(f"\n\n{'=' * 60}")
                _logger.info(f"PROCESSING COMPANY: {company.name} (ID: {company.id})")
                _logger.info(f"{'=' * 60}")

                try:
                    # Check if company has required configuration
                    if not company.erpc_stock_journal_id:
                        _logger.error(f"❌ Missing Stock Journal for {company.name}")
                        failed_companies += 1
                        continue

                    if not company.erpc_stock_variation_account_id:
                        _logger.error(f"❌ Missing Stock Variation Account for {company.name}")
                        failed_companies += 1
                        continue

                    if not company.erpc_stock_value_account_id:
                        _logger.error(f"❌ Missing Stock Value Account for {company.name}")
                        failed_companies += 1
                        continue

                    # Get current day data
                    domain_current = [
                        ('create_date', '<=', today_end),
                        ('product_id.type', '=', 'product'),
                        ('categ_id', '!=', 19),
                        ('company_id', '=', company.id),
                    ]

                    _logger.info(f"Current data domain: {domain_current}")

                    grouped_data_current = self.read_group(
                        domain=domain_current,
                        fields=['brand_id', 'value:sum'],
                        groupby=['brand_id'],
                        lazy=False
                    )

                    _logger.info(f"Found {len(grouped_data_current)} brand groups for current data")

                    # Process current data
                    total_current = 0
                    processed_current = []

                    for group in grouped_data_current:
                        brand_value = round(group.get('value', 0))
                        total_current += brand_value

                        brand_info = {
                            'brand_id': group.get('brand_id', [False, 'No Brand'])[0],
                            'brand_name': group.get('brand_id', [False, 'No Brand'])[1],
                            'value': brand_value,
                        }
                        processed_current.append(brand_info)

                    _logger.info(f"💰 Total Current Stock Value: {total_current}")

                    # Get previous day data
                    domain_previous = [
                        ('create_date', '<=', yesterday_end),
                        ('product_id.type', '=', 'product'),
                        ('categ_id', '!=', 19),
                        ('company_id', '=', company.id),
                    ]

                    grouped_data_previous = self.read_group(
                        domain=domain_previous,
                        fields=['brand_id', 'value:sum'],
                        groupby=['brand_id'],
                        lazy=False
                    )

                    _logger.info(f"Found {len(grouped_data_previous)} brand groups for previous data")

                    # Process previous data
                    total_previous = 0
                    processed_previous = []

                    for group in grouped_data_previous:
                        brand_value = round(group.get('value', 0))
                        total_previous += brand_value

                        brand_info = {
                            'brand_id': group.get('brand_id', [False, 'No Brand'])[0],
                            'brand_name': group.get('brand_id', [False, 'No Brand'])[1],
                            'value': brand_value,
                        }
                        processed_previous.append(brand_info)

                    _logger.info(f"💰 Total Previous Stock Value: {total_previous}")

                    # Skip if no data for both periods
                    if total_current == 0 and total_previous == 0:
                        _logger.info(f"⚠️ No stock data found for {company.name}, skipping...")
                        continue

                    # Build analytic distributions - FIXED: Remove company_id from brand search
                    analytic_distribution_current = self._build_analytic_distribution(
                        processed_current, total_current, company, "CURRENT"
                    )

                    analytic_distribution_previous = self._build_analytic_distribution(
                        processed_previous, total_previous, company, "PREVIOUS"
                    )

                    # Create accounting entries
                    move_created = self._create_accounting_entries(
                        company,
                        total_current,
                        total_previous,
                        analytic_distribution_current,
                        analytic_distribution_previous,
                        today_end,
                        yesterday_end
                    )

                    if move_created:
                        successful_companies += 1
                        _logger.info(f"✅ SUCCESS: Created accounting entry for {company.name}")
                    else:
                        failed_companies += 1
                        _logger.error(f"❌ FAILED: Could not create accounting entry for {company.name}")

                except Exception as e:
                    failed_companies += 1
                    _logger.error(f"❌ ERROR processing {company.name}: {str(e)}")
                    _logger.error(f"Traceback:", exc_info=True)
                    continue

            # Final summary
            _logger.info(f"\n\n{'=' * 60}")
            _logger.info(f"PROCESSING COMPLETE")
            _logger.info(f"Successful: {successful_companies}")
            _logger.info(f"Failed: {failed_companies}")
            _logger.info(f"Total: {len(all_companies)}")
            _logger.info(f"{'=' * 60}")

            return successful_companies > 0

        except Exception as e:
            _logger.error(f"❌ CRITICAL ERROR in main function: {str(e)}")
            _logger.error(f"Traceback:", exc_info=True)
            return False

    def _build_analytic_distribution(self, brand_data, total_value, company, period_name):
        """Build analytic distribution from brand data - FIXED VERSION"""
        _logger.info(f"Building analytic distribution for {period_name} period")

        analytic_distribution = {}

        for brand_info in brand_data:
            brand_name = brand_info['brand_name']
            brand_value = brand_info['value']

            if brand_value == 0:
                continue

            # Calculate percentage
            percentage = round((brand_value / abs(total_value)) * 100, 2) if total_value != 0 else 0

            # FIXED: Remove company_id filter since product.brand doesn't have company_id field
            brand = self.env['product.brand'].sudo().search([
                ('name', '=', brand_name),
            ], limit=1)

            if brand and brand.analytic_account_id:
                analytic_account_id = brand.analytic_account_id.id
                if analytic_account_id in analytic_distribution:
                    analytic_distribution[analytic_account_id] += percentage
                else:
                    analytic_distribution[analytic_account_id] = percentage
                _logger.info(f"  - Brand '{brand_name}': {percentage}% -> Account {analytic_account_id}")
            else:
                _logger.warning(f"  - Brand '{brand_name}': No analytic account found")

        # Add "To ALL Depts." account

        to_all_depts = self.env['account.analytic.account'].sudo().search([
            # ('company_id', '=', company.id),# TO DO uncomment this line if branch has its analytic distribution
            ('name', '=', 'To ALL Depts.'),
            ('plan_id.name', '=', 'Department')
        ], limit=1)

        if to_all_depts:
            analytic_distribution[to_all_depts.id] = 100
            _logger.info(f"  - Added 'To ALL Depts.' account: {to_all_depts.id}")
        else:
            _logger.warning(f"  - 'To ALL Depts.' account not found for company {company.name}")

        _logger.info(f"Final analytic distribution: {analytic_distribution}")
        return analytic_distribution

    def _create_accounting_entries(self, company, total_current, total_previous,
                                   analytic_distribution_current, analytic_distribution_previous,
                                   today_end, yesterday_end):
        """Create the actual accounting entries"""
        try:
            move_lines = []

            stock_journal_id = company.erpc_stock_journal_id
            stock_variation_account_id = company.erpc_stock_variation_account_id
            stock_value_account_id = company.erpc_stock_value_account_id

            _logger.info(f"Creating accounting lines for {company.name}")
            _logger.info(f"Journal: {stock_journal_id.name}")
            _logger.info(f"Variation Account: {stock_variation_account_id.code}")
            _logger.info(f"Value Account: {stock_value_account_id.code}")

            # Create cancellation entries for previous day
            if total_previous != 0:
                move_lines.append((0, 0, {
                    'account_id': stock_variation_account_id.id,
                    'analytic_distribution': analytic_distribution_previous,
                    'currency_id': company.currency_id.id,
                    'debit': total_previous,
                    'credit': 0.0,
                    'name': f'CANCELLATION - Previous Stock {yesterday_end.date()}',
                }))
                move_lines.append((0, 0, {
                    'account_id': stock_value_account_id.id,
                    'currency_id': company.currency_id.id,
                    'debit': 0.0,
                    'credit': total_previous,
                    'name': f'CANCELLATION - Previous Stock {yesterday_end.date()}',
                }))
                _logger.info(f"Created cancellation entries for {total_previous}")

            # Create current day entries
            if total_current != 0:
                move_lines.append((0, 0, {
                    'account_id': stock_value_account_id.id,
                    'currency_id': company.currency_id.id,
                    'debit': total_current,
                    'credit': 0.0,
                    'name': f'CREATION - Current Stock {today_end.date()}',
                }))
                move_lines.append((0, 0, {
                    'account_id': stock_variation_account_id.id,
                    'analytic_distribution': analytic_distribution_current,
                    'currency_id': company.currency_id.id,
                    'debit': 0.0,
                    'credit': total_current,
                    'name': f'CREATION - Current Stock {today_end.date()}',
                }))
                _logger.info(f"Created current entries for {total_current}")

            if not move_lines:
                _logger.warning("No accounting lines to create")
                return False

            # Create the accounting entry
            move_vals = {
                'move_type': 'entry',
                'company_id': company.id,
                'journal_id': stock_journal_id.id,
                'date': today_end.date(),
                'ref': _('Stock Variation - %s - %s') % (today_end.strftime('%Y-%m-%d'), company.name),
                'line_ids': move_lines,
            }

            _logger.info(f"Creating account move with vals: {move_vals}")

            variation_entry = self.env['account.move'].sudo().create(move_vals)

            # Update company's last inventory value
            company.erpc_last_inventory_value = total_current

            # Post the entry
            variation_entry._post(soft=True)

            _logger.info(f"✅ Accounting entry created and posted: {variation_entry.name}")
            return True

        except Exception as e:
            _logger.error(f"❌ Error creating accounting entries: {str(e)}")
            return False