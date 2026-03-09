from odoo import api, models, fields, _
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round, date_utils, convert_file, format_amount

from odoo.exceptions import UserError
from odoo.tools import format_date
import logging


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    date_from = fields.Date(
        string='From', readonly=False, required=True,
        compute="_compute_date_from", store=True, precompute=True)
    date_to = fields.Date(
        string='To', readonly=False, required=True,
        compute="_compute_date_to", store=True, precompute=True)

    @api.depends('payslip_run_id')
    def _compute_date_from(self):
        for payslip in self:
            if payslip.payslip_run_id:
                payslip.date_from = payslip.payslip_run_id.date_start
            elif self.env.context.get('default_date_from'):
                payslip.date_from = self.env.context.get('default_date_from')
            else:
                payslip.date_from = payslip._get_schedule_period_start()

    @api.depends('date_from', 'payslip_run_id')
    def _compute_date_to(self):
        for payslip in self:
            if payslip.payslip_run_id:
                payslip.date_to = payslip.payslip_run_id.date_end
            elif self.env.context.get('default_date_to'):
                payslip.date_to = self.env.context.get('default_date_to')
            else:
                payslip.date_to = payslip.date_from and payslip.date_from + payslip._get_schedule_timedelta()

            if payslip.version_id and payslip.version_id.date_end and payslip.date_from >= payslip.version_id.date_start \
                    and payslip.date_from < payslip.version_id.date_end and payslip.date_to > payslip.version_id.date_end:
                payslip.date_to = payslip.contrversion_idaversion_idct_id.date_end

    # Fields related to the contract and employee
    contract_start_date = fields.Date("Contract Start Date", related="version_id.date_start", store=True)
    contract_end_date = fields.Date("Contract End Date", related="version_id.date_end", store=True)
    department_id = fields.Many2one('hr.department', "Department", related="employee_id.department_id", store=True)

    # Salary computation fields
    transportation = fields.Float('Transportation', compute='_compute_salary_components', store=True)
    allowances_bonus = fields.Float('Bonus Allowances', compute='_compute_salary_components', store=True)
    allowances_commission = fields.Float('Incentive Allowances', compute='_compute_salary_components', store=True)
    allowances_scholarship = fields.Float('NSSF_Scholarship', compute='_compute_salary_components', store=True)
    nssf_representation_fees = fields.Float('NSSF_Representation Fees', compute='_compute_salary_components', store=True)
    allowances_value_medical = fields.Float('Value Medical Allowances', compute='_compute_salary_components',
                                            store=True)
    allowances_value_goods = fields.Float('Value Goods Allowances', compute='_compute_salary_components', store=True)
    allowances_exceptional = fields.Float('Exceptional Allowances', compute='_compute_salary_components', store=True)
    deduction_exceptional = fields.Float('Exceptional Deduction', compute='_compute_salary_components', store=True)
    deduction_advance = fields.Float('Short Advance', compute='_compute_salary_components', store=True)
    deduction_loan = fields.Float('Long Advance', compute='_compute_salary_components', store=True)
    deduction_goods = fields.Float('Goods Deduction', compute='_compute_salary_components', store=True)
    overtime = fields.Float('Overtime', compute='_compute_salary_components', store=True)
    undertime = fields.Float('Undertime', compute='_compute_salary_components', store=True)
    net_to_pay = fields.Float('Net To Pay', compute='_compute_salary_components', store=True)
    net_value = fields.Float('Net Value', compute='_compute_salary_components', store=True)
    unpaid = fields.Float('Unpaid', compute='_compute_salary_components', store=True)

    basic_nssf_usd = fields.Float('NSSF_Basic (USD)', compute='_compute_salary_components', store=True)
    basic_nssf_lbp = fields.Float('NSSF_Basic (LBP)', compute='_compute_salary_components', store=True)
    nssf_additional_on_salary = fields.Float('NSSF_Additional on Salary', compute='_compute_salary_components', store=True)
    nssf_medical_insurance = fields.Float('NSSF_Medical Insurance', compute='_compute_salary_components', store=True)
    nssf_allowances_home = fields.Float('NSSF_Home Allowances', compute='_compute_salary_components', store=True)
    nssf_total_salary = fields.Float('NSSF_Total Salary B4 Abat', compute='_compute_salary_components', store=True)
    nssf_abattement = fields.Float('NSSF_Abattement', compute='_compute_salary_components', store=True)
    nssf_taxable_salary = fields.Float('NSSF_Taxable Salary', compute='_compute_salary_components', store=True)
    nssf_tax_on_salary = fields.Float('NSSF_Tax on Salary', compute='_compute_salary_components', store=True)
    attendance = fields.Float('Attendance', compute='_compute_salary_components', store=True)
    transportation_nssf = fields.Float('NSSF_Transportation', compute='_compute_salary_components', store=True)
    nssf_3_sickness_salary = fields.Float('NSSF_3% Sickness Salary', compute='_compute_salary_components', store=True)
    nssf_8_sickness_salary = fields.Float('NSSF_8% Sickness Salary', compute='_compute_salary_components', store=True)
    sickness_cotisation_8_nssf = fields.Float('NSSF_8% Sickness Cotisation Company', compute='_compute_salary_components',
                                              store=True)
    sickness_cotisation_3_nssf = fields.Float('NSSF_3% Sickness Contribution Employee', compute='_compute_salary_components',
                                              store=True)
    sickness_cotisation_11_nssf = fields.Float('NSSF_11% Sickness Contribution (Company and Employee)', compute='_compute_salary_components',
                                               store=True)
    end_of_service_8_5_nssf = fields.Float('NSSF_8.5% End of Service Contribution Company', compute='_compute_salary_components',
                                           store=True)
    nssf_8_5_end_of_service = fields.Float('NSSF_8.5% End of Service Salary', compute='_compute_salary_components',
                                           store=True)
    family_allowance_cont_comp_6_nssf = fields.Float('NSSF_6% Family Allowance Contribution Company', compute='_compute_salary_components',
                                                     store=True)
    family_allowance_6_nssf = fields.Float('NSSF_6% Family Allowance Salary', compute='_compute_salary_components',
                                           store=True)
    nssf_total_cotisation_tbp = fields.Float('NSSF_Total Cotisation to be Paid', compute='_compute_salary_components',
                                             store=True)
    nssf_net_to_pay = fields.Float('NSSF_Net To Pay', compute='_compute_salary_components',
                                   store=True)
    nssf_net_value = fields.Float('NSSF_Net Value', compute='_compute_salary_components',
                                  store=True)
    nssf_net_value_2 = fields.Float('Forfait NSSF Net Value', compute='_compute_salary_components',
                                    store=True)
    difference_forfait = fields.Float('Difference Forfait', compute='_compute_salary_components',
                                      store=True)
    family_allowance_employee_nssf = fields.Float('NSSF_Family Allowance (Kids and Partner)',
                                                  compute='_compute_salary_components', store=True)

    @api.depends('line_ids')
    def _compute_salary_components(self):
        for payslip in self:
            # Initialize fields
            payslip.transportation = payslip._get_rule_total('TRNS')
            payslip.allowances_bonus = payslip._get_rule_total('BON')
            payslip.allowances_commission = payslip._get_rule_total('COM')
            payslip.allowances_scholarship = payslip._get_rule_total('SCHL')
            payslip.nssf_representation_fees = payslip._get_rule_total('RF')
            payslip.allowances_value_medical = payslip._get_rule_total('MEDINS')
            payslip.allowances_value_goods = payslip._get_rule_total('AGDS')
            payslip.allowances_exceptional = payslip._get_rule_total('EXPL')
            payslip.deduction_exceptional = payslip._get_rule_total('DED')
            payslip.deduction_advance = payslip._get_rule_total('ADV')
            payslip.deduction_loan = payslip._get_rule_total('CLO')
            payslip.deduction_goods = payslip._get_rule_total('DGDS')

            payslip.overtime = payslip._get_rule_total('OVR_TIME')
            payslip.undertime = payslip._get_rule_total('UND_TIME')
            payslip.net_to_pay = payslip._get_rule_total('NETTOPAY')
            payslip.net_value = payslip._get_rule_total('NETVAL')
            payslip.unpaid = payslip._get_rule_total('UNPD')

            payslip.basic_nssf_usd = payslip._get_rule_total('BASICNUSD')
            # payslip.basic_nssf_lbp = payslip._get_rule_total('BASICLBP')
            if payslip.employee_id.id == 178 and payslip.employee_id.is_representation_fees:
                payslip.basic_nssf_lbp = payslip._get_rule_total('BASICLBPM')
            else:
                payslip.basic_nssf_lbp = payslip._get_rule_total('BASICLBP')
            payslip.nssf_additional_on_salary = payslip._get_rule_total('NSSFAD')
            payslip.nssf_medical_insurance = payslip._get_rule_total('MEDNSSF')
            payslip.nssf_allowances_home = payslip._get_rule_total('HOMEALW')
            payslip.nssf_total_salary = payslip._get_rule_total('TOTALSAL')
            payslip.nssf_abattement = payslip._get_rule_total('ABATT')
            payslip.nssf_taxable_salary = payslip._get_rule_total('TXSAL')
            payslip.nssf_tax_on_salary = payslip._get_rule_total('TDLBP')
            payslip.attendance = payslip._get_rule_days('WORK_HOURS')

            payslip.transportation_nssf = payslip._get_rule_total('TRNSNSSF')
            payslip.nssf_3_sickness_salary = payslip._get_rule_total('3SSAL')
            payslip.nssf_8_sickness_salary = payslip._get_rule_total('8SSAL')
            payslip.sickness_cotisation_11_nssf = payslip._get_rule_total('11SC')
            payslip.sickness_cotisation_8_nssf = payslip._get_rule_total('DCC')
            payslip.sickness_cotisation_3_nssf = payslip._get_rule_total('NSSFEMP')
            payslip.end_of_service_8_5_nssf = payslip._get_rule_total('NSSFCOMP')
            payslip.nssf_8_5_end_of_service = payslip._get_rule_total('8.5FASAL')
            payslip.family_allowance_cont_comp_6_nssf = payslip._get_rule_total('FAC')
            payslip.family_allowance_6_nssf = payslip._get_rule_total('6FASAL')
            payslip.nssf_total_cotisation_tbp = payslip._get_rule_total('TCP')
            # payslip.nssf_net_to_pay = payslip._get_rule_total('NSSFTOPAY')
            if payslip.employee_id.id == 178 and payslip.employee_id.is_representation_fees:
                payslip.nssf_net_to_pay = payslip._get_rule_total('NSSFTOPAYM')
            else:
                payslip.nssf_net_to_pay = payslip._get_rule_total('NSSFTOPAY')
            payslip.nssf_net_value = payslip._get_rule_total('NSSFTOVAL')
            payslip.nssf_net_value_2 = payslip._get_rule_total('NSSFNETVAL')
            payslip.difference_forfait = payslip._get_rule_total('DFO')
            payslip.family_allowance_employee_nssf = payslip._get_rule_total('FA')

    def _get_rule_total(self, code):
        """
        Helper method to calculate the total amount of a specific rule code from line_ids.
        """
        rule_lines = self.line_ids.filtered(lambda line: line.code == code)
        return sum(rule_lines.mapped('total'))

    def _get_rule_days(self, code):
        worked_days = self.worked_days_line_ids.filtered(lambda wd: wd.code == code)

        return sum(worked_days.mapped('number_of_days'))

    bmr_currency = fields.Many2one('res.currency', "BMR Currency", related='company_id.bmr_currency', store=True)
    bmr_currency_rate = fields.Float("BMR Currency Rate", compute='_compute_bmr_currency_rate', store=True)
    official_currency = fields.Many2one('res.currency', string="Official Currency",
                                        related='company_id.official_currency', store=True)
    official_currency_rate = fields.Float("Official Currency Rate", compute='_compute_official_currency_rate',
                                          store=True)
    category = fields.Selection([
        ('with_commission', 'With Commission'),
        ('without_commission', 'Without Commission')
    ], string='Category', related='version_id.category', store=True)
    # usd_rate = fields.Float('USD Basic Rate', digits=(16, 2), related='version_id.usd_rate', store=True)
    # lbp_rate = fields.Float('LBP Basic Rate', digits=(16, 2), related='version_id.lbp_rate', store=True)
    # overtime = fields.Float('Overtime', compute='_compute_salary')
    # undertime = fields.Float('Undertime', compute='_compute_salary')
    # basic_salary = fields.Float('Basic Salary', compute='_compute_salary')

    work_location_id = fields.Many2one('hr.work.location', "Work Location", related='employee_id.work_location_id',
                                       store=True)

    # @api.depends('version_id')
    # def _compute_salary(self):
    #     for rec in self:
    #         # rec.basic_salary = rec.version_id.contract_wage
    #         rec.overtime = 0
    #         rec.undertime = 0
    #         # salary_difference = round(rec.basic_salary - rec.basic_wage, 2)
    #         if salary_difference > 0:
    #             rec.undertime = salary_difference
    #         else:
    #             rec.overtime = abs(salary_difference)

    @api.depends('bmr_currency')
    def _compute_bmr_currency_rate(self):
        for payslip in self:
            if payslip.bmr_currency:
                payslip.bmr_currency_rate = payslip.bmr_currency.rate
            else:
                payslip.bmr_currency_rate = 0

    @api.depends('official_currency')
    def _compute_official_currency_rate(self):
        for payslip in self:
            if payslip.official_currency:
                payslip.official_currency_rate = payslip.official_currency.rate
            else:
                payslip.official_currency_rate = 0

    @api.model
    def create(self, values):
        payslips = super(Payslip, self).create(values)
        bmr_currency_rate = self.env.context.get('bmr_currency_rate', False)
        if bmr_currency_rate:
            for payslip in payslips:
                payslip.bmr_currency_rate = bmr_currency_rate

        return payslips

    # Removing the warning

    @api.depends("date_from", "date_to", "struct_id")
    def _compute_warning_message(self):
        for slip in self.filtered(lambda p: p.date_to):
            slip.warning_message = False
            warnings = []
            if slip.version_id and (
                    slip.date_from < slip.version_id.date_start
                    or (
                            slip.version_id.date_end
                            and slip.date_to > slip.version_id.date_end
                    )
            ):
                warnings.append(
                    _(
                        "The period selected does not match the contract validity period."
                    )
                )

            if slip.date_to > date_utils.end_of(fields.Date.today(), "month"):
                warnings.append(
                    _(
                        "Work entries may not be generated for the period from %(start)s to %(end)s.",
                        start=date_utils.add(
                            date_utils.end_of(fields.Date.today(), "month"), days=1
                        ),
                        end=slip.date_to,
                    )
                )

            # if (
            #     slip.version_id.schedule_pay
            #     or slip.version_id.structure_type_id.default_schedule_pay
            # ) and slip.date_from + slip._get_schedule_timedelta() != slip.date_to:
            #     warnings.append(
            #         _(
            #             "The duration of the payslip is not accurate according to the structure type."
            #         )
            #     )

            if warnings:
                warnings = [_("This payslip can be erroneous :")] + warnings
                slip.warning_message = "\n  ・ ".join(warnings)
