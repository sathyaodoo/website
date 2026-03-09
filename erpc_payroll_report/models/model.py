from odoo import models, fields, api


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    matching_input_description = fields.Char(
        string="Matching Input Description",
        compute="_compute_matching_input_description",
    )

    def _compute_matching_input_description(self):
        for line in self:
            # Filter input lines matching the name of the payslip line
            matching_inputs = line.slip_id.input_line_ids.filtered(lambda input: input.input_type_id.name == line.name)

            if matching_inputs:
                # Find the input line with the closest amount to the payslip line's amount
                closest_input = min(
                    matching_inputs,
                    key=lambda input: abs(input.amount - line.amount)
                )
                # Assign the description of the closest matching input
                line.matching_input_description = closest_input.name
            else:
                # No matching inputs found
                line.matching_input_description = False
