from odoo import models, fields, api, tools, Command, _


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    medical_line_id = fields.Many2one('medical.value.allowance', string="Medical Value Allowance", help="Medical Value Allowance")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.depends('employee_id', 'version_id', 'struct_id', 'date_from', 'date_to', 'struct_id')
    def _compute_input_line_ids(self):
        res = super()._compute_input_line_ids()
        for slip in self:
            if not slip.employee_id or not slip.date_from or not slip.date_to:
                continue

            lines_to_remove = slip.input_line_ids.filtered(lambda line_id: line_id.medical_line_id)
            slip.update({'input_line_ids': [Command.unlink(line.id) for line in lines_to_remove]})

            input_type_id = self.env['hr.payslip.input.type'].search([('code', '=', 'MEDINS')])
            medical_ids = self.env['medical.value.allowance'].search([
                ('employee_id', '=', slip.employee_id.id),
                ('date', '>=', slip.date_from),
                ('date', '<=', slip.date_to),
                ('paid', '=', False)
            ])
            for medical_id in medical_ids:
                slip.input_line_ids = [Command.create({
                    'input_type_id': input_type_id.id,
                    'medical_line_id': medical_id.id,
                    'amount': medical_id.medical_value_allowance,
                    'name': 'Medical Value Allowances',
                })]
        return res

    def action_payslip_done(self):
        medical_input_line_ids = self.input_line_ids.filtered(lambda line_id: line_id.medical_line_id)
        hr_medical_ids = medical_input_line_ids.mapped('medical_line_id')
        hr_medical_ids.write({'paid': True})

        return super(HrPayslip, self).action_payslip_done()
