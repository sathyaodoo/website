from odoo import api, models, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        working_hours_work_entry_type_id = self.env.ref('erpc_daily_attendance.erpc_hr_work_entry_type_working_hours')
        res = super(HrPayslip, self)._get_worked_day_lines()

        # We will use the variable i to avoid having the "out of range" error
        i = -1
        for line in res:
            i += 1
            if 'work_entry_type_id' in line.keys() and line['work_entry_type_id'] == working_hours_work_entry_type_id.id:
                res.pop(i)
                i -= 1

        for rec in self:
            hours_per_day = rec._get_worked_day_lines_hours_per_day()

            # Get Worked Hours
            self.env.cr.execute(f"""
                SELECT
                    COUNT(*) AS number_of_days,
                   SUM(erpc_hr_daily_attendance.planned_work_hours) AS t_planned_work_hours
                FROM
                   erpc_hr_daily_attendance
                WHERE
                   erpc_hr_daily_attendance.employee_id = {rec.employee_id.id}
                       AND erpc_hr_daily_attendance.attendance_type = 'present'
                       AND erpc_hr_daily_attendance.state not in ('cancelled')
                       AND erpc_hr_daily_attendance.attendance_date BETWEEN '{rec.date_from}' AND '{rec.date_to}'
           """)
            number_of_days, t_worked_hours = self.env.cr.fetchone()
            t_worked_hours = t_worked_hours or 0
            number_of_days = number_of_days or 0
            if t_worked_hours:
                res.append({
                    'sequence': 50,
                    'work_entry_type_id': working_hours_work_entry_type_id.id,
                    'number_of_days': number_of_days,
                    'number_of_hours': t_worked_hours,
                })

            # Get overtime and undertime
            self.env.cr.execute(f"""
                SELECT
                    SUM(erpc_hr_daily_attendance.overtime) AS t_overtime,
                    SUM(erpc_hr_daily_attendance.undertime) AS t_undertime
                FROM
                    erpc_hr_daily_attendance
                WHERE
                    erpc_hr_daily_attendance.employee_id = {rec.employee_id.id}
                        AND erpc_hr_daily_attendance.state not in ('cancelled')
                        AND erpc_hr_daily_attendance.attendance_date BETWEEN '{rec.date_from}' AND '{rec.date_to}'
            """)
            t_overtime, t_undertime = self.env.cr.fetchone()
            t_overtime = t_overtime or 0
            t_undertime = t_undertime or 0
            t_difference = t_overtime - t_undertime
            # t_overtime = t_difference if t_difference > 0 else 0
            # t_undertime = abs(t_difference) if t_difference < 0 else 0

            if t_overtime:
                overtime_work_entry_type_id = self.env.ref('erpc_daily_attendance.erpc_hr_work_entry_type_overtime')
                days_overtime = round(t_overtime / hours_per_day, 5) if hours_per_day else 0
                r_days_overtime = rec._round_days(overtime_work_entry_type_id, days_overtime)
                res.append({
                    'sequence': 50,
                    'work_entry_type_id': overtime_work_entry_type_id.id,
                    'number_of_days': r_days_overtime,
                    'number_of_hours': t_overtime,
                })

            if t_undertime:
                undertime_work_entry_type_id = self.env.ref('erpc_daily_attendance.erpc_hr_work_entry_type_undertime')
                days_undertime = round(t_undertime / hours_per_day, 5) if hours_per_day else 0
                r_days_undertime = rec._round_days(undertime_work_entry_type_id, days_undertime)
                res.append({
                    'sequence': 50,
                    'work_entry_type_id': undertime_work_entry_type_id.id,
                    'number_of_days': r_days_undertime * -1,
                    'number_of_hours': t_undertime * -1,
                })
        return res


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    
    @api.depends('work_entry_type_id', 'number_of_days', 'number_of_hours', 'payslip_id')
    def _compute_name(self):
        to_check_public_holiday = {
            res[0]: res[1]
            for res in self.env['resource.calendar.leaves']._read_group(
                [
                    ('resource_id', '=', False),
                    ('work_entry_type_id', 'in', self.mapped('work_entry_type_id').ids),
                    ('date_from', '<=', max(self.payslip_id.mapped('date_to'))),
                    ('date_to', '>=', min(self.payslip_id.mapped('date_from'))),
                ],
                ['work_entry_type_id'],
                ['id:recordset']
            )
        }
        for worked_days in self:
            public_holidays = to_check_public_holiday.get(worked_days.work_entry_type_id, '')
            holidays = public_holidays and public_holidays.filtered(lambda p:
               (p.calendar_id.id == worked_days.payslip_id.version_id.resource_calendar_id.id or not p.calendar_id.id)
                and p.date_from.date() <= worked_days.payslip_id.date_to
                and p.date_to.date() >= worked_days.payslip_id.date_from
                and p.company_id == worked_days.payslip_id.company_id)
            half_day = worked_days._is_half_day()
            if holidays:
                name = (', '.join(holidays.mapped('name')))
            else:
                name = worked_days.work_entry_type_id.name
            worked_days.name = name 


    @api.depends('is_paid', 'number_of_hours', 'payslip_id', 'version_id.wage', 'payslip_id.sum_worked_hours')
    def _compute_amount(self):
        for worked_days in self:
            if worked_days.payslip_id.edited or worked_days.payslip_id.state not in ['draft', 'verify']:
                continue
            if not worked_days.version_id or worked_days.code == 'OUT':
                worked_days.amount = 0
                continue
            if worked_days.payslip_id.wage_type == "hourly":
                worked_days.amount = worked_days.payslip_id.contract_id.hourly_wage * worked_days.number_of_hours if worked_days.is_paid else 0
            else:
                employee_hourly_cost = worked_days.payslip_id.employee_id.hourly_cost
                if worked_days.work_entry_type_id.id == self.env.ref('erpc_daily_attendance.erpc_hr_work_entry_type_working_hours').id:
                    worked_days.amount = worked_days.payslip_id.version_id.contract_wage
                elif worked_days.work_entry_type_id.id == self.env.ref('erpc_daily_attendance.erpc_hr_work_entry_type_overtime').id:
                    worked_days.amount = employee_hourly_cost * worked_days.number_of_hours * 1.5
                elif worked_days.work_entry_type_id.id == self.env.ref('erpc_daily_attendance.erpc_hr_work_entry_type_undertime').id:
                    worked_days.amount = employee_hourly_cost * worked_days.number_of_hours
                elif worked_days.work_entry_type_id.id == self.env.ref('hr_work_entry.work_entry_type_unpaid_leave').id:
                    worked_days.amount = employee_hourly_cost * worked_days.number_of_hours * -1
                else:
                    worked_days.amount = 0
