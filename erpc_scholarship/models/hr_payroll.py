from odoo import models, fields, api, tools, Command, _


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    scholarship_line_id = fields.Many2one('hr.scholarship', string="Scholarship", help="Scholarship")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.depends('employee_id', 'version_id', 'struct_id', 'date_from', 'date_to')
    def _compute_input_line_ids(self):
        res = super()._compute_input_line_ids()
        for slip in self:
            if not slip.employee_id or not slip.date_from or not slip.date_to:
                continue

            lines_to_remove = slip.input_line_ids.filtered(lambda l: l.scholarship_line_id)
            slip.update({'input_line_ids': [Command.unlink(line.id) for line in lines_to_remove]})

            input_type_id = self.env['hr.payslip.input.type'].search([('code', '=', 'SCHL')], limit=1)
            scholarship_ids = self.env['hr.scholarship'].search([
                ('employee_id', '=', slip.employee_id.id),
                ('date', '>=', slip.date_from),
                ('date', '<=', slip.date_to),
                ('paid', '=', False),
            ])
            for scholarship in scholarship_ids:
                slip.input_line_ids = [Command.create({
                    'input_type_id': input_type_id.id,
                    'scholarship_line_id': scholarship.id,
                    'amount': scholarship.scholarship_amount,
                    'name': scholarship.name,
                })]

                scholarship.write({
                    'payslip_id': slip.id,
                    'batch_id': slip.payslip_run_id.id if slip.payslip_run_id else False,
                })

        return res

    def action_payslip_done(self):
        scholarship_input_line_ids = self.input_line_ids.filtered(lambda l: l.scholarship_line_id)
        hr_scholarship_ids = scholarship_input_line_ids.mapped('scholarship_line_id')
        hr_scholarship_ids.write({'paid': True})
        return super().action_payslip_done()