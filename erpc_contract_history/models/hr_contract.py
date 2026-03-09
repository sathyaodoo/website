from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class HrVersion(models.Model):
    _inherit = 'hr.version'

    history_ids = fields.One2many('erpc.hr.contract.history', 'contract_id', string="Contract History", ondelete='cascade')
    nssf_wage = fields.Float('NSSF Wage')
    nssf_wage_lbp = fields.Float('NSSF Wage LBP')
    nssf_entry_date = fields.Date('NSSF Entry Date')
    nssf_leave_date = fields.Date('NSSF Leave Date')
    r3_delivery_date = fields.Date('R3 Delivery Date')

    @api.model
    def update_contract_and_close_old_history(self):
        """Scheduled action to close old contract history and update contract details when needed"""
        today = fields.Date.today()

        contracts = self.env['hr.version'].search([])

        for contract in contracts:
            contract_histories = self.env['erpc.hr.contract.history'].sudo().search([
                ('contract_id', '=', contract.id),
            ], order='date_from asc')

            if contract_histories:
                for i in range(len(contract_histories) - 1):
                    current_history = contract_histories[i]
                    next_history = contract_histories[i + 1]

                    if today == next_history.date_from - timedelta(days=1) and not current_history.date_to:
                        current_history.sudo().write({
                            'date_to': today
                        })

                latest_valid_history = self.env['erpc.hr.contract.history'].sudo().search([
                    ('contract_id', '=', contract.id),
                    ('date_from', '<=', today),
                ], order='date_from desc', limit=1)

                if latest_valid_history:
                    update_values = {
                        'wage': latest_valid_history.wage,
                        'currency_id': latest_valid_history.currency_id.id,
                        'department_id': latest_valid_history.department_id.id,
                        'job_id': latest_valid_history.job_id.id,
                    }

                    # Check if `resource_calendar_id` is not False before writing
                    if latest_valid_history.resource_calendar_id:
                        update_values['resource_calendar_id'] = latest_valid_history.resource_calendar_id.id

                    contract.sudo().write(update_values)

    @api.constrains('history_ids')
    def _check_history_dates(self):
        for contract in self:
            sorted_history = contract.history_ids.sorted(lambda h: h.date_from)
            for i in range(len(sorted_history) - 1):
                if sorted_history[i].date_to > sorted_history[i + 1].date_from:
                    raise UserError(
                        "The 'Date To' of a history record cannot be greater than the 'Date From' of the next record.")

    def update_contract(self):
        today = fields.Date.today()

        contracts = self.env['hr.version'].search([])

        for contract in contracts:
            contract_histories = self.env['erpc.hr.contract.history'].sudo().search([
                ('contract_id', '=', contract.id),
            ], order='date_from asc')

            if contract_histories:
                for i in range(len(contract_histories) - 1):
                    current_history = contract_histories[i]
                    next_history = contract_histories[i + 1]

                    if today == next_history.date_from - timedelta(days=1) and not current_history.date_to:
                        current_history.sudo().write({
                            'date_to': today
                        })

                latest_valid_history = self.env['erpc.hr.contract.history'].sudo().search([
                    ('contract_id', '=', contract.id),

                ], order='date_from desc', limit=1)

                if latest_valid_history:
                    update_values = {
                        'wage': latest_valid_history.wage,
                        'currency_id': latest_valid_history.currency_id.id,
                        'department_id': latest_valid_history.department_id.id,
                        'job_id': latest_valid_history.job_id.id,
                    }

                    # Check if `resource_calendar_id` is not False before writing
                    if latest_valid_history.resource_calendar_id:
                        update_values['resource_calendar_id'] = latest_valid_history.resource_calendar_id.id

                    contract.sudo().write(update_values)
