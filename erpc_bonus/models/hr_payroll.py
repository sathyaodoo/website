from odoo import models, fields, api, tools, Command, _


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    bonus_line_id = fields.Many2one('hr.bonus', string="Bonus", help="Bonus")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.depends('employee_id', 'version_id', 'struct_id', 'date_from', 'date_to', 'struct_id')
    def _compute_input_line_ids(self):
        res = super()._compute_input_line_ids()
        for slip in self:
            if not slip.employee_id or not slip.date_from or not slip.date_to:
                continue

            lines_to_remove = slip.input_line_ids.filtered(lambda line_id: line_id.bonus_line_id)
            slip.update({'input_line_ids': [Command.unlink(line.id) for line in lines_to_remove]})

            input_type_id = self.env['hr.payslip.input.type'].search([('code', '=', 'BON')])
            bonus_ids = self.env['hr.bonus'].search([
                ('employee_id', '=', slip.employee_id.id),
                ('date', '>=', slip.date_from),
                ('date', '<=', slip.date_to),
                ('paid', '=', False)
            ])
            for bonus_id in bonus_ids:
                slip.input_line_ids = [Command.create({
                    'input_type_id': input_type_id.id,
                    'bonus_line_id': bonus_id.id,
                    'amount': bonus_id.bonus_amount,
                    'name': 'Bonus',
                })]

                bonus_id.write({
                    'payslip_id': slip.id,
                    'batch_id': slip.payslip_run_id.id if slip.payslip_run_id else False,
                })

        return res

    def action_payslip_done(self):
        bonus_input_line_ids = self.input_line_ids.filtered(lambda line_id: line_id.bonus_line_id)
        hr_bonus_ids = bonus_input_line_ids.mapped('bonus_line_id')
        hr_bonus_ids.write({'paid': True})

        return super(HrPayslip, self).action_payslip_done()
