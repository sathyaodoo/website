import json
from odoo import models
from odoo.exceptions import UserError
import logging

_log = logging.getLogger(__name__)


class PartnerLedgerReportNew(models.AbstractModel):
    _name = 'report.erpc_customer_statement_report.partner_ledger_report'
    _description = 'customer statement'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['partner.ledger.wizard'].browse(self.env.context.get('active_ids'))
        _log.info(f'\n\n\n\n*****data xslx*******{data}\n\n\n\n.')
        format1 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': True, 'border': True, })
        bold = workbook.add_format({'bold': True, 'align': 'center', 'border': True, 'bg_color': '#D3D3D3'})
        # Add format for numbers
        num_format = '#,##0.000'
        clr = workbook.add_format({'align': 'center', 'border': True, 'num_format': num_format})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})


        # Add format for numbers with thousand separators and two decimal places
        format_number = workbook.add_format({'align': 'right', 'num_format': num_format})
        # sheet 1
        sheet1 = workbook.add_worksheet('sheet1')
        sheet1.set_column('B:B', 40, )
        sheet1.set_column('C:C', 30, )
        # sheet1.set_column('D:D', 40, )

        sheet1.write(3, 1, 'Date From' + str(data.date_from), bold)
        sheet1.write(3, 4, 'Date To' + str(data.date_to), bold)

        sheet1.write(6, 0, 'Date', bold)
        sheet1.write(6, 1, 'Customer Name', bold)
        sheet1.write(6, 2, 'Voucher', bold)
        sheet1.write(6, 3, 'Debit', bold)
        sheet1.write(6, 4, 'Credit', bold)
        sheet1.write(6, 5, 'Balance', bold)
        sheet1.write(6, 6, 'Currency', bold)

        row = 7
        balance = 0.00
        debit = 0.00
        credit = 0.00
        account_move_line = []
        [account_move_line.append(line) for line in
         self.env['account.move.line'].search([('date', '>=', data.date_from), ('date', '<=', data.date_to)])]

        _log.info(f'\n\n\n\n*****account_move_line xslx*******{account_move_line}\n\n\n\n.')

        if data.account_type == 'customer':
            account_move_line = list(filter(lambda
                                                self: self.account_id.account_type == 'asset_receivable', account_move_line))
            _log.info(f'\n\n\n\n*****account_move_line customer xslx*******{account_move_line}\n\n\n\n.')

        elif data.account_type == 'payable':
            account_move_line = list(filter(
                lambda self: self.account_id.account_type == 'liability_payable', account_move_line))
            _log.info(f'\n\n\n\n*****account_move_line payable xslx*******{account_move_line}\n\n\n\n.')

        elif data.account_type == 'customer_supplier':
            account_move_line = list(filter(lambda self: self.account_id.account_type in ['asset_receivable', 'liability_payable'], account_move_line))
            _log.info(f'\n\n\n\n*****account_move_line customer_supplier xslx*******{account_move_line}\n\n\n\n.')

        if data.target_move == 'posted':
            account_move_line = list(filter(lambda self: self.move_id.state == 'posted', account_move_line))

        elif data.target_move == 'all':
            account_move_line = list(filter(lambda
                                                self: self.move_id.state == 'posted' or self.move_id.state == 'draft' or self.move_id.state == 'cancel',
                                            account_move_line))

        if data.currency_id:
            account_move_line = list(filter(lambda self: self.currency_id.id == data.currency_id.id, account_move_line))

        if data.customer_ids:
            account_move_line = list(
                filter(lambda self: self.move_id.partner_id.id in data.customer_ids.ids, account_move_line))

        # if not data.with_null_amount_residual:
        #     account_move_line = list(
        #         filter(lambda self: self.amount_residual != 0, account_move_line))

        if not data.with_null_amount_residual:
            account_move_line = [line for line in account_move_line if line.amount_residual != 0]

        # account_move_line = sorted(account_move_line, key=lambda line: line.date)
        account_move_line = sorted(account_move_line, key=lambda line: (line.date, line.id))
        # account_move_line = sorted(account_move_line, key=lambda line: (line.date, line.move_id.name))

        for entry in account_move_line:
            entry_date = entry.date
            if entry.debit != 0:
                balance = entry.amount_currency + balance
                amount = entry.amount_currency
                debit = entry.debit + debit
                # sheet1.write(row, 0, str(entry.date), clr)
                sheet1.write(row, 0, entry_date, date_format)
                sheet1.write(row, 1, entry.partner_id.name, clr)
                sheet1.write(row, 2, entry.move_id.name, clr)
                sheet1.write(row, 3, amount, clr)
                # sheet1.write(row, 4, '', clr)
                sheet1.write(row, 4, 0.000, clr)
                sheet1.write(row, 5, balance, clr)
                sheet1.write(row, 6, entry.currency_id.name, clr)

                row += 1
            elif entry.credit != 0:
                balance = entry.amount_currency + balance
                amount = entry.amount_currency
                credit = entry.credit + credit
                # sheet1.write(row, 0, str(entry.date), clr)
                sheet1.write(row, 0, entry_date, date_format)
                sheet1.write(row, 1, entry.partner_id.name, clr)
                sheet1.write(row, 2, entry.move_id.name, clr)
                sheet1.write(row, 3, 0.000, clr)
                # sheet1.write(row, 4, '', clr)
                sheet1.write(row, 4, abs(amount), clr)
                sheet1.write(row, 5, balance, clr)
                sheet1.write(row, 6, entry.currency_id.name, clr)

                row += 1

        row += 1
        # sheet1.write(row, 2, 'Total', bold)
        # sheet1.write(row, 3, debit, bold)
        # sheet1.write(row, 4, credit, bold)
        # sheet1.write(row, 5, balance, bold)

        sheet1.write(row, 2, 'Total', bold)
        sheet1.write_formula(row, 3, '=SUM(D8:D{})'.format(row - 1), clr)
        sheet1.write_formula(row, 4, '=SUM(E8:E{})'.format(row - 1), clr)
        sheet1.write_formula(row, 5, '=D{}-E{}'.format(row + 1, row + 1), clr)
