from odoo import models, fields, api, tools, Command, _

import logging

_logger = logging.getLogger(__name__)


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    deduction_line_id = fields.Many2one('hr.deduction', string="Deduction", readonly=True)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.depends('employee_id', 'version_id', 'struct_id', 'date_from', 'date_to', 'struct_id')
    def _compute_input_line_ids(self):
        res = super()._compute_input_line_ids()
        for slip in self:
            if not slip.employee_id or not slip.date_from or not slip.date_to:
                continue

            lines_to_remove = slip.input_line_ids.filtered(lambda line_id: line_id.deduction_line_id)
            slip.update({'input_line_ids': [Command.unlink(line.id) for line in lines_to_remove]})

            input_type_id = self.env['hr.payslip.input.type'].search([('code', '=', 'DED')])
            deduction_ids = self.env['hr.deduction'].search([
                ('employee_id', '=', slip.employee_id.id),
                ('date', '>=', slip.date_from),
                ('date', '<=', slip.date_to),
                ('paid', '=', False)
            ])
            for deduction_id in deduction_ids:
                slip.input_line_ids = [Command.create({
                    'input_type_id': input_type_id.id,
                    'deduction_line_id': deduction_id.id,
                    'amount': deduction_id.deduction_amount,
                    'name': 'Deduction',
                })]
        return res

    def action_payslip_done(self):
        deduction_input_line_ids = self.input_line_ids.filtered(lambda line_id: line_id.deduction_line_id)
        hr_deduction_ids = deduction_input_line_ids.mapped('deduction_line_id')
        hr_deduction_ids.write({'paid': True})

        return super(HrPayslip, self).action_payslip_done()
