from odoo import models, fields, api, tools, Command, _


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    add_allowances_line_id = fields.Many2one('hr.additional.allowances', string="Additional Allowances",
                                             help="Additional Allowances")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # to fix
    # @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to', 'struct_id')
    def _compute_input_line_ids(self):
        res = super()._compute_input_line_ids()
        for slip in self:
            if not slip.employee_id or not slip.date_from or not slip.date_to:
                continue

            lines_to_remove = slip.input_line_ids.filtered(lambda line_id: line_id.add_allowances_line_id)
            slip.update({'input_line_ids': [Command.unlink(line.id) for line in lines_to_remove]})

            input_type_id = self.env['hr.payslip.input.type'].search([('code', '=', 'ADDALW')])
            allowances_ids = self.env['hr.additional.allowances'].search([
                ('employee_id', '=', slip.employee_id.id),
                ('date', '>=', slip.date_from),
                ('date', '<=', slip.date_to),
                ('paid', '=', False)
            ])
            for allow_id in allowances_ids:
                slip.input_line_ids = [Command.create({
                    'input_type_id': input_type_id.id,
                    'add_allowances_line_id': allow_id.id,
                    'amount': allow_id.add_allowances_amount,
                    'name': 'Additional Allowances',
                })]

                allow_id.write({
                    'payslip_id': slip.id,
                    'batch_id': slip.payslip_run_id.id if slip.payslip_run_id else False,
                })

        return res

    def action_payslip_done(self):
        allowances_input_line_ids = self.input_line_ids.filtered(lambda line_id: line_id.add_allowances_line_id)
        hr_allowances_ids = allowances_input_line_ids.mapped('add_allowances_line_id')
        hr_allowances_ids.write({'paid': True})

        return super(HrPayslip, self).action_payslip_done()
