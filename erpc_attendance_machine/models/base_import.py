from odoo import api, models, fields, _
from datetime import datetime
from dateutil import tz

import logging

log = logging.getLogger(__name__)


class Import(models.TransientModel):
    _inherit = 'base_import.import'

    def _parse_import_data(self, data, import_fields, options):
        if self.res_model in ('attendance.offline', 'attendance.biotime'):
            final_data = []
            utc_timezone = tz.gettz('UTC')

            for row in data:
                id_employee_device = ""
                utc_datetime = ""
                if self.res_model == 'attendance.offline':
                    id_employee_device = row[0].strip()  # id_employee_device
                    employee_timezone = tz.gettz(self.env['hr.employee'].search([('device_id', '=', id_employee_device)]).tz)
                    datetime_string = row[1]  # datetime
                    etz_datetime = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S").replace(tzinfo=employee_timezone)  # adding timezone information to datetime
                    utc_datetime = etz_datetime.astimezone(utc_timezone).replace(tzinfo=None)  # changing timezone utc and removing timezone info

                if self.res_model == 'attendance.biotime':
                    id_employee_device = row[0]  # id_employee_device
                    employee_timezone = tz.gettz(self.env['hr.employee'].search([('device_id', '=', id_employee_device)]).tz)
                    date_string = row[2]  # date
                    time_string = row[3]  # time
                    datetime_string = date_string + ' ' + time_string
                    etz_datetime = datetime.strptime(datetime_string, "%m/%d/%Y %H:%M:%S").replace(tzinfo=employee_timezone)  # adding timezone information to datetime
                    utc_datetime = etz_datetime.astimezone(utc_timezone).replace(tzinfo=None)  # changing timezone utc and removing timezone info

                # Prevent duplicates in the model by adding to the final data only the records that its id_employee_device and datetime does not already exist
                record_exists = self.env[self.res_model].search([
                    ('id_employee_device', '=', id_employee_device),
                    ('datetime', '=', utc_datetime),
                ])
                if not record_exists:
                    final_data.append(row)

            return super(Import, self)._parse_import_data(final_data, import_fields, options)
        return super(Import, self)._parse_import_data(data, import_fields, options)
