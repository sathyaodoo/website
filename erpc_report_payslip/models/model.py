from odoo import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.depends('employee_id', 'struct_id', 'date_to')
    def _compute_name(self):
        for slip in self.filtered(lambda p: p.employee_id and p.date_to):
            lang = slip.employee_id.lang or self.env.user.lang
            context = {'lang': lang}
            payslip_name = slip.struct_id.payslip_name or _('Salary Slip')
            del context
            # Format the payslip name using only date_to
            slip.name = '%(payslip_name)s - %(employee_name)s - %(date_to)s' % {
                'payslip_name': payslip_name,
                'employee_name': slip.employee_id.name,
                'date_to': slip.date_to.strftime('%B %Y'),
            }