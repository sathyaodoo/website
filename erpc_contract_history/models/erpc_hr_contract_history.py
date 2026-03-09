from odoo import models, fields, api


class ContractHistory(models.Model):
    _name = 'erpc.hr.contract.history'
    _description = 'Contract History'
    _order = 'id desc'

    contract_id = fields.Many2one('hr.version', string='Contract', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To')
    wage = fields.Monetary(string='Wage')
    currency_id = fields.Many2one('res.currency', string='Currency')
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Job')
    description = fields.Char('Description')
    resource_calendar_id = fields.Many2one(
        'resource.calendar', 'Working Schedule')
    employee_id = fields.Many2one("hr.employee", related="contract_id.employee_id", store=True)

    @api.model
    def default_get(self, fields_list):
        defaults = super(ContractHistory, self).default_get(fields_list)
        context = self._context
        contract_id = context.get('default_contract_id', False)
        if contract_id:
            contract = self.env['hr.version'].browse(contract_id)
            defaults.update({
                'contract_start': contract.date_start,
                'contract_end': contract.date_end,
                'wage': contract.wage,
                'currency_id': contract.currency_id.id,
                'department_id': contract.department_id.id,
                'job_id': contract.job_id.id,
            })
        return defaults
