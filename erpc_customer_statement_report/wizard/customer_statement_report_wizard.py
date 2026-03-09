from odoo import api, fields, models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import logging

_log = logging.getLogger(__name__)


class PartnerLedgerReport(models.TransientModel):
    _name = "partner.ledger.wizard"
    _description = "customer statement"

    date_from = fields.Date(string='From Date', required=True, default='1990-01-01')
    date_to = fields.Date(string='Date to', required=True, default=datetime.today())
    customer_ids = fields.Many2many('res.partner', string='Customers')
    currency_id = fields.Many2one('res.currency', 'Currency')
    account_type = fields.Selection([
        ('customer', 'Receivable Account'),
        ('payable', 'Payable Accounts'),
        ('customer_supplier', 'Receivable and Payable Accounts'),
    ], string="Partner's Type", required=True, default='customer_supplier')
    target_move = fields.Selection([
        ('posted', 'All Posted Entries'),
        ('all', 'All Entries'),
    ], default='posted')
    with_initial_balance = fields.Boolean()
    with_null_amount_residual= fields.Boolean()

    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to', 'customer_ids'])[0]
        _log.info(f'\n\n\n\n*****Dataaaaa***1111****{data}\n\n\n\n.')
        return self._print_report(data)

    def print_report_fc(self):
        data = self[0].read()
        if 'active_ids' in self._context:
            data[0].update({'active_ids': self._context['active_ids']})
        return self.env.ref('erpc_customer_statement_report.action_report_partnerledger').report_action(self,
                                                                                             data={'form': data[0]})

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to', 'customer_ids'])[0])
        _log.info(f'\n\n\n\n*****Dataaaaa*******{data}\n\n\n\n.')
        return self.env.ref('erpc_customer_statement_report.partner_ledger_report').report_action(self, data=data,
                                                                                                config=False)

