import tempfile
import xlsxwriter
from odoo import models, fields, api
import base64
import logging

_logger = logging.getLogger(__name__)


class MyWizard(models.TransientModel):
    _name = 'account.debit.credit.wizard'

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    account_root = fields.Many2many("account.root", string='Account root', required=False)
    partner_id = fields.Many2one('res.partner', string='Partner')
    excel_file = fields.Binary(string='Excel File', readonly=True)
    excel_file_name = fields.Char(string='Excel Filename', readonly=True)

    def generate_excel(self, data, company_name, from_date, to_date):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            workbook = xlsxwriter.Workbook(temp_file.name)

            # Define formats
            header_format = workbook.add_format({'bold': True})
            title_format = workbook.add_format({'bold': True, 'font_size': 14})
            date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
            comma_format = workbook.add_format({'num_format': '#,##0.00'})

            # Create a worksheet and write data
            worksheet = workbook.add_worksheet("Report")

            # Freeze panes: Freeze the first 4 rows and first 1 column (0-indexed)
            worksheet.freeze_panes(4, 4)

            # Set column widths (adjust as necessary)
            worksheet.set_column('A:Y', 15)

            row = 0

            # Write the company name and date range
            worksheet.write(row, 0, company_name, title_format)
            row += 1
            worksheet.write(row, 0, f"From: {from_date.strftime('%d/%m/%Y')} To: {to_date.strftime('%d/%m/%Y')}",
                            date_format)
            row += 2  # Add an extra empty row for spacing

            # Write headers
            headers = [
                'Account Code', 'Account Name', 'Partner', 'Partner/External Id', 'Currency', 'Initial Amount In currency', 'Initial Debit',
                'Initial Credit',
                'Initial Balance',
                'Initial Second Debit', 'Initial Second Credit', 'Initial Second Balance', 'Total Amount in Currency',
                'Total Debit', 'Total Credit', 'Balance', 'Second Debit', 'Second Credit', 'Second Balance',
                'End Amount in Currency', 'Residual in currency',
                'End Debit', 'End Credit', 'End Balance', 'Residual', 'End Second Debit', 'End Second Credit',
                'End Second Balance',
                'Analytic Distribution'
            ]
            for col_num, header in enumerate(headers):
                worksheet.write(row, col_num, header, header_format)

            # Increment row for data
            row += 1

            # Write data
            for entry in data:
                worksheet.write(row, 0, entry['account_code'])
                worksheet.write(row, 1, entry['account_name'])
                worksheet.write(row, 2, entry['partner_name'])
                worksheet.write(row, 3, entry['partner_external_id'])
                worksheet.write(row, 4, entry['currency'])
                worksheet.write(row, 5, entry['initial_amount_in_currency'], comma_format)
                worksheet.write(row, 6, entry['initial_debit'], comma_format)
                worksheet.write(row, 7, entry['initial_credit'], comma_format)
                worksheet.write(row, 8, entry['initial_balance'], comma_format)
                worksheet.write(row, 9, entry['initial_second_debit'], comma_format)
                worksheet.write(row, 10, entry['initial_second_credit'], comma_format)
                worksheet.write(row, 11, entry['initial_second_balance'], comma_format)
                worksheet.write(row, 12, entry['bet_amount_in_currency'], comma_format)
                worksheet.write(row, 13, entry['bet_debit'], comma_format)
                worksheet.write(row, 14, entry['bet_credit'], comma_format)
                worksheet.write(row, 15, entry['bet_balance'], comma_format)
                worksheet.write(row, 16, entry['bet_second_debit'], comma_format)
                worksheet.write(row, 17, entry['bet_second_credit'], comma_format)
                worksheet.write(row, 18, entry['bet_second_balance'], comma_format)
                worksheet.write(row, 19, entry['end_amount_in_currency'], comma_format)
                worksheet.write(row, 20, entry['amount_residual'], comma_format)
                worksheet.write(row, 21, entry['end_debit'], comma_format)
                worksheet.write(row, 22, entry['end_credit'], comma_format)
                worksheet.write(row, 23, entry['end_balance'], comma_format)
                worksheet.write(row, 24, entry['amount_residual_currency'], comma_format)
                worksheet.write(row, 25, entry['end_second_debit'], comma_format)
                worksheet.write(row, 26, entry['end_second_credit'], comma_format)
                worksheet.write(row, 27, entry['end_second_balance'], comma_format)
                row += 1

            workbook.close()

            with open(temp_file.name, 'rb') as excel_file:
                excel_data = excel_file.read()

            return excel_data

    def print_data_excel(self):
        try:
            # Build SQL query
            query = """
                WITH initial_balances AS (
                    SELECT
                        aa.code as account_code,
                        aa.name as account_name,
                        rp.name as partner_name,
                        COALESCE((SELECT imd.module || '.' || imd.name FROM ir_model_data imd 
                                 WHERE imd.model = 'res.partner' AND imd.res_id = rp.id 
                                 ORDER BY imd.id DESC LIMIT 1), '') as partner_external_id,
                        rc.name as currency,
                        SUM(aml.amount_currency) as initial_amount_in_currency,
                        SUM(aml.debit) as initial_debit,
                        SUM(aml.credit) as initial_credit,
                        SUM(aml.balance) as initial_balance,
                        SUM(aml.amount_residual_currency) as ini_amount_residual_currency,
                        SUM(aml.amount_residual) as ini_amount_residual,
                        SUM(aml.second_debit_id) as initial_second_debit,
                        SUM(aml.second_credit_id) as initial_second_credit,
                        SUM(aml.second_debit_id - aml.second_credit_id) as initial_second_balance
                    FROM 
                        account_move_line aml
                    JOIN 
                        account_account aa ON aml.account_id = aa.id
                    LEFT JOIN 
                        res_partner rp ON aml.partner_id = rp.id
                    LEFT JOIN 
                        res_currency rc ON aml.currency_id = rc.id
                    WHERE 
                        aml.date < %s
                        AND aml.company_id = %s
                        AND aml.parent_state = 'posted'
                        AND aml.partner_id IS NOT NULL
                        {account_root_condition}
                        {partner_condition}
                    GROUP BY
                        aa.code, aa.name, rp.name, rp.id, rc.name
                ), between_balances AS (
                    SELECT
                        aa.code as account_code,
                        aa.name as account_name,
                        rp.name as partner_name,
                        COALESCE((SELECT imd.module || '.' || imd.name FROM ir_model_data imd 
                                 WHERE imd.model = 'res.partner' AND imd.res_id = rp.id 
                                 ORDER BY imd.id DESC LIMIT 1), '') as partner_external_id,
                        rc.name as currency,
                        SUM(aml.amount_currency) as bet_amount_in_currency,
                        SUM(aml.debit) as bet_debit,
                        SUM(aml.credit) as bet_credit,
                        SUM(aml.balance) as bet_balance,
                        SUM(aml.amount_residual_currency) as bet_amount_residual_currency,
                        SUM(aml.amount_residual) as bet_amount_residual,
                        SUM(aml.second_debit_id) as bet_second_debit,
                        SUM(aml.second_credit_id) as bet_second_credit,
                        SUM(aml.second_debit_id - aml.second_credit_id) as bet_second_balance
                    FROM 
                        account_move_line aml
                    JOIN 
                        account_account aa ON aml.account_id = aa.id
                    LEFT JOIN 
                        res_partner rp ON aml.partner_id = rp.id
                    LEFT JOIN 
                        res_currency rc ON aml.currency_id = rc.id
                    WHERE 
                        aml.date BETWEEN %s AND %s
                        AND aml.company_id = %s
                        AND aml.parent_state = 'posted'
                        AND aml.partner_id IS NOT NULL
                        {account_root_condition}
                        {partner_condition}
                    GROUP BY
                        aa.code, aa.name, rp.name, rp.id, rc.name
                )

                SELECT 
                    aa.code as account_code,
                    aa.name as account_name,
                    rp.name as partner_name,
                    COALESCE((SELECT imd.module || '.' || imd.name FROM ir_model_data imd 
                             WHERE imd.model = 'res.partner' AND imd.res_id = rp.id 
                             ORDER BY imd.id DESC LIMIT 1), '') as partner_external_id,
                    rc.name as currency,
                    COALESCE(initial_balances.initial_amount_in_currency, 0) as initial_amount_in_currency,
                    COALESCE(initial_balances.initial_debit, 0) as initial_debit,
                    COALESCE(initial_balances.initial_credit, 0) as initial_credit,
                    COALESCE(initial_balances.initial_balance, 0) as initial_balance,
                    COALESCE(initial_balances.initial_second_debit, 0) as initial_second_debit,
                    COALESCE(initial_balances.initial_second_credit, 0) as initial_second_credit,
                    COALESCE(initial_balances.initial_second_balance, 0) as initial_second_balance,
                    COALESCE(between_balances.bet_amount_in_currency, 0) as bet_amount_in_currency,
                    COALESCE(between_balances.bet_debit, 0) as bet_debit,
                    COALESCE(between_balances.bet_credit, 0) as bet_credit,
                    COALESCE(between_balances.bet_balance, 0) as bet_balance,
                    COALESCE(between_balances.bet_second_debit, 0) as bet_second_debit,
                    COALESCE(between_balances.bet_second_credit, 0) as bet_second_credit,
                    COALESCE(between_balances.bet_second_balance, 0) as bet_second_balance,
                    COALESCE(initial_balances.initial_amount_in_currency, 0) + COALESCE(between_balances.bet_amount_in_currency, 0) as end_amount_currency,  
                    COALESCE(initial_balances.ini_amount_residual_currency, 0) + COALESCE(between_balances.bet_amount_residual_currency, 0) as amount_residual_currency,
                    COALESCE(between_balances.bet_debit, 0) + COALESCE(initial_balances.initial_debit, 0) as end_debit,
                    COALESCE(between_balances.bet_credit, 0) + COALESCE(initial_balances.initial_credit, 0) as end_credit,
                    COALESCE(initial_balances.initial_balance, 0) + COALESCE(between_balances.bet_balance, 0) as end_balance,
                    COALESCE(initial_balances.ini_amount_residual, 0) + COALESCE(between_balances.bet_amount_residual, 0) as amount_residual,
                    COALESCE(between_balances.bet_second_debit, 0) + COALESCE(initial_balances.initial_second_debit, 0) as end_second_debit,
                    COALESCE(between_balances.bet_second_credit, 0) + COALESCE(initial_balances.initial_second_credit, 0) as end_second_credit,
                    COALESCE(initial_balances.initial_second_balance, 0) + COALESCE(between_balances.bet_second_balance, 0) as end_second_balance
                FROM 
                    account_move_line aml
                JOIN 
                    account_account aa ON aml.account_id = aa.id
                LEFT JOIN 
                    res_partner rp ON aml.partner_id = rp.id
                LEFT JOIN 
                    res_currency rc ON aml.currency_id = rc.id
                LEFT JOIN
                    initial_balances ON aa.code = initial_balances.account_code 
                    AND aa.name = initial_balances.account_name 
                    AND rp.name = initial_balances.partner_name 
                    AND COALESCE((SELECT imd.module || '.' || imd.name FROM ir_model_data imd 
                                WHERE imd.model = 'res.partner' AND imd.res_id = rp.id 
                                ORDER BY imd.id DESC LIMIT 1), '') = initial_balances.partner_external_id
                    AND rc.name = initial_balances.currency
                LEFT JOIN
                    between_balances ON aa.code = between_balances.account_code 
                    AND aa.name = between_balances.account_name 
                    AND rp.name = between_balances.partner_name 
                    AND COALESCE((SELECT imd.module || '.' || imd.name FROM ir_model_data imd 
                                WHERE imd.model = 'res.partner' AND imd.res_id = rp.id 
                                ORDER BY imd.id DESC LIMIT 1), '') = between_balances.partner_external_id
                    AND rc.name = between_balances.currency
                WHERE 
                    aml.company_id = %s
                    AND aml.parent_state = 'posted'
                    AND aml.partner_id IS NOT NULL
                    {account_root_condition}
                    {partner_condition}
                GROUP BY
                    aa.code, aa.name, rp.name, rp.id, rc.name,
                    initial_balances.initial_amount_in_currency,
                    initial_balances.initial_debit, initial_balances.initial_credit, initial_balances.initial_balance,
                    initial_balances.initial_second_debit, initial_balances.initial_second_credit, initial_balances.initial_second_balance, 
                    initial_balances.ini_amount_residual, between_balances.bet_amount_residual, initial_balances.ini_amount_residual_currency, 
                    between_balances.bet_amount_residual_currency,
                    between_balances.bet_amount_in_currency, between_balances.bet_debit, between_balances.bet_credit, between_balances.bet_balance,
                    between_balances.bet_second_debit, between_balances.bet_second_credit, between_balances.bet_second_balance
                ORDER BY
                    aa.code, aa.name, rp.name, rc.name
            """
            if not self.partner_id:
                query_without_partner = """
                    WITH initial_balances AS (
                        SELECT
                            aa.code as account_code,
                            aa.name as account_name,
                            rc.name as currency,
                            SUM(aml.amount_currency) as initial_amount_in_currency,
                            SUM(aml.debit) as initial_debit,
                            SUM(aml.credit) as initial_credit,
                            SUM(aml.balance) as initial_balance,
                            SUM(aml.amount_residual_currency) as ini_amount_residual_currency,
                            SUM(aml.amount_residual) as ini_amount_residual,
                            SUM(aml.second_debit_id) as initial_second_debit,
                            SUM(aml.second_credit_id) as initial_second_credit,
                            SUM(aml.second_debit_id - aml.second_credit_id) as initial_second_balance
                        FROM 
                            account_move_line aml
                        JOIN 
                            account_account aa ON aml.account_id = aa.id
                        LEFT JOIN 
                            res_currency rc ON aml.currency_id = rc.id
                        WHERE 
                            aml.date < %s
                            AND aml.company_id = %s
                            AND aml.parent_state = 'posted'
                            AND aml.partner_id IS NULL
                            {account_root_condition}
                        GROUP BY
                            aa.code, aa.name, rc.name
                    ), between_balances AS (
                        SELECT
                            aa.code as account_code,
                            aa.name as account_name,
                            rc.name as currency,
                            SUM(aml.amount_currency) as bet_amount_in_currency,
                            SUM(aml.debit) as bet_debit,
                            SUM(aml.credit) as bet_credit,
                            SUM(aml.balance) as bet_balance,
                            SUM(aml.amount_residual_currency) as bet_amount_residual_currency,
                            SUM(aml.amount_residual) as bet_amount_residual,
                            SUM(aml.second_debit_id) as bet_second_debit,
                            SUM(aml.second_credit_id) as bet_second_credit,
                            SUM(aml.second_debit_id - aml.second_credit_id) as bet_second_balance
                        FROM 
                            account_move_line aml
                        JOIN 
                            account_account aa ON aml.account_id = aa.id
                        LEFT JOIN 
                            res_currency rc ON aml.currency_id = rc.id
                        WHERE 
                            aml.date BETWEEN %s AND %s
                            AND aml.company_id = %s
                            AND aml.parent_state = 'posted'
                            AND aml.partner_id IS NULL
                            {account_root_condition}
                        GROUP BY
                            aa.code, aa.name, rc.name
                    )

                    SELECT 
                        aa.code as account_code,
                        aa.name as account_name,
                        rc.name as currency,
                        COALESCE(initial_balances.initial_amount_in_currency, 0) as initial_amount_in_currency,
                        COALESCE(initial_balances.initial_debit, 0) as initial_debit,
                        COALESCE(initial_balances.initial_credit, 0) as initial_credit,
                        COALESCE(initial_balances.initial_balance, 0) as initial_balance,
                        COALESCE(initial_balances.initial_second_debit, 0) as initial_second_debit,
                        COALESCE(initial_balances.initial_second_credit, 0) as initial_second_credit,
                        COALESCE(initial_balances.initial_second_balance, 0) as initial_second_balance,
                        COALESCE(between_balances.bet_amount_in_currency, 0) as bet_amount_in_currency,
                        COALESCE(between_balances.bet_debit, 0) as bet_debit,
                        COALESCE(between_balances.bet_credit, 0) as bet_credit,
                        COALESCE(between_balances.bet_balance, 0) as bet_balance,
                        COALESCE(between_balances.bet_second_debit, 0) as bet_second_debit,
                        COALESCE(between_balances.bet_second_credit, 0) as bet_second_credit,
                        COALESCE(between_balances.bet_second_balance, 0) as bet_second_balance,
                        COALESCE(initial_balances.initial_amount_in_currency, 0) + COALESCE(between_balances.bet_amount_in_currency, 0) as end_amount_currency,  
                        COALESCE(initial_balances.ini_amount_residual_currency, 0) + COALESCE(between_balances.bet_amount_residual_currency, 0) as amount_residual_currency,
                        COALESCE(between_balances.bet_debit, 0) + COALESCE(initial_balances.initial_debit, 0) as end_debit,
                        COALESCE(between_balances.bet_credit, 0) + COALESCE(initial_balances.initial_credit, 0) as end_credit,
                        COALESCE(initial_balances.initial_balance, 0) + COALESCE(between_balances.bet_balance, 0) as end_balance,
                        COALESCE(initial_balances.ini_amount_residual, 0) + COALESCE(between_balances.bet_amount_residual, 0) as amount_residual,
                        COALESCE(between_balances.bet_second_debit, 0) + COALESCE(initial_balances.initial_second_debit, 0) as end_second_debit,
                        COALESCE(between_balances.bet_second_credit, 0) + COALESCE(initial_balances.initial_second_credit, 0) as end_second_credit,
                        COALESCE(initial_balances.initial_second_balance, 0) + COALESCE(between_balances.bet_second_balance, 0) as end_second_balance
                    FROM 
                        account_move_line aml
                    JOIN 
                        account_account aa ON aml.account_id = aa.id
                    LEFT JOIN 
                        res_currency rc ON aml.currency_id = rc.id
                    LEFT JOIN
                        initial_balances ON aa.code = initial_balances.account_code 
                        AND aa.name = initial_balances.account_name
                        AND rc.name = initial_balances.currency
                    LEFT JOIN
                        between_balances ON aa.code = between_balances.account_code 
                        AND aa.name = between_balances.account_name
                        AND rc.name = between_balances.currency
                    WHERE 
                        aml.company_id = %s
                        AND aml.parent_state = 'posted'
                        AND aml.partner_id IS NULL
                        {account_root_condition}
                    GROUP BY
                        aa.code, aa.name, rc.name,
                        initial_balances.initial_amount_in_currency,
                        initial_balances.initial_debit, initial_balances.initial_credit, initial_balances.initial_balance,
                        initial_balances.initial_second_debit, initial_balances.initial_second_credit, initial_balances.initial_second_balance, 
                        initial_balances.ini_amount_residual, between_balances.bet_amount_residual, initial_balances.ini_amount_residual_currency, 
                        between_balances.bet_amount_residual_currency,
                        between_balances.bet_amount_in_currency, between_balances.bet_debit, between_balances.bet_credit, between_balances.bet_balance,
                        between_balances.bet_second_debit, between_balances.bet_second_credit, between_balances.bet_second_balance
                    ORDER BY
                        aa.code, aa.name, rc.name
                """

            # Add condition for account prefix if provided
            account_root_codes = [root.name for root in self.account_root]

            # Initialize conditions and base params
            account_root_condition = ""
            partner_condition = ""
            params = [self.from_date, self.env.company.id]

            # Build the account_root_condition and append values to params
            if self.account_root:
                account_root_condition = "AND (" + " OR ".join(["aa.code LIKE %s" for _ in account_root_codes]) + ")"
                account_root_values = [f"{code}%" for code in account_root_codes]
                params += account_root_values

            if self.partner_id:
                partner_condition = "AND rp.id = %s"
                partner_id = self.partner_id.id
                params += [partner_id]

            params += [self.from_date, self.to_date, self.env.company.id]

            if self.account_root:
                params += account_root_values

            if self.partner_id:
                params += [partner_id]

            params += [self.env.company.id]

            if self.account_root:
                params += account_root_values

            if self.partner_id:
                params += [partner_id]

            _logger.info("Params after adding conditions: %s", params)

            # Format the query with the conditions
            query = query.format(account_root_condition=account_root_condition, partner_condition=partner_condition)
            if not self.partner_id:
                query_without_partner = query_without_partner.format(account_root_condition=account_root_condition)

            # Execute the first query
            self.env.cr.execute(query, tuple(params))
            result = self.env.cr.fetchall()

            # Execute the second query
            if not self.partner_id:
                self.env.cr.execute(query_without_partner, tuple(params))
                result_without_partners = self.env.cr.fetchall()

                _logger.info(
                    "Query executed successfully. Retrieved %d rows from the first query and %d rows from the second query.",
                    len(result), len(result_without_partners))

            # Prepare data in the format required by generate_excel
            data = []
            user_lang = self.env.user.lang or 'en_US'

            # Process first query results
            for row in result:
                account_name = row[1]
                if isinstance(account_name, dict):
                    account_name = account_name.get(user_lang, account_name.get('en_US', ''))
                data.append({
                    'account_code': row[0],
                    'account_name': account_name,
                    'partner_name': row[2],
                    'partner_external_id': row[3],
                    'currency': row[4],
                    'initial_amount_in_currency': row[5],
                    'initial_debit': row[6],
                    'initial_credit': row[7],
                    'initial_balance': row[8],
                    'initial_second_debit': row[9],
                    'initial_second_credit': row[10],
                    'initial_second_balance': row[11],
                    'bet_amount_in_currency': row[12],
                    'bet_debit': row[13],
                    'bet_credit': row[14],
                    'bet_balance': row[15],
                    'bet_second_debit': row[16],
                    'bet_second_credit': row[17],
                    'bet_second_balance': row[18],
                    'end_amount_in_currency': row[19],
                    'amount_residual_currency': row[20],
                    'end_debit': row[21],
                    'end_credit': row[22],
                    'end_balance': row[23],
                    'amount_residual': row[24],
                    'end_second_debit': row[25],
                    'end_second_credit': row[26],
                    'end_second_balance': row[27],
                })

            # Process second query results and append to the same data list
            if not self.partner_id:
                for col in result_without_partners:
                    account_name = col[1]
                    if isinstance(account_name, dict):
                        account_name = account_name.get(user_lang, account_name.get('en_US', ''))
                    data.append({
                        'account_code': col[0],
                        'account_name': account_name,
                        'partner_name': '',
                        'partner_external_id': '',
                        'currency': col[2],
                        'initial_amount_in_currency': col[3],
                        'initial_debit': col[4],
                        'initial_credit': col[5],
                        'initial_balance': col[6],
                        'initial_second_debit': col[7],
                        'initial_second_credit': col[8],
                        'initial_second_balance': col[9],
                        'bet_amount_in_currency': col[10],
                        'bet_debit': col[11],
                        'bet_credit': col[12],
                        'bet_balance': col[13],
                        'bet_second_debit': col[14],
                        'bet_second_credit': col[15],
                        'bet_second_balance': col[16],
                        'end_amount_in_currency': col[17],
                        'amount_residual_currency': col[18],
                        'end_debit': col[19],
                        'end_credit': col[20],
                        'end_balance': col[21],
                        'amount_residual': col[22],
                        'end_second_debit': col[23],
                        'end_second_credit': col[24],
                        'end_second_balance': col[25],
                    })

            # Generate Excel file with combined data
            excel_file = self.generate_excel(data, self.env.company.name, self.from_date, self.to_date)

            self.excel_file = base64.b64encode(excel_file)
            self.excel_file_name = 'debit_credit_SOA.xlsx'

            action = {
                'type': 'ir.actions.act_url',
                'url': '/web/content/?model=account.debit.credit.wizard&id=%s&field=excel_file&filename_field=excel_file_name&download=true&filename=debit_credit_soa.xlsx' % self.id,
                'target': 'self',
            }
        except Exception as e:
            _logger.error("Error generating Excel report: %s", str(e))
            action = {
                'type': 'ir.actions.act_window',
                'res_model': 'account.debit.credit.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_from_date': self.from_date,
                            'default_to_date': self.to_date},
                'warning': {
                    'title': 'Error',
                    'message': str(e),
                },
            }

        return action