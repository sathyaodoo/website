from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil import tz
# from zk import ZK

import logging

log = logging.getLogger(__name__)


class ZkMachine(models.Model):
    _name = 'zk.machine'

    name = fields.Char("Machine", required=True)
    machine_ip = fields.Char("IP/DNS", required=True)
    port_num = fields.Integer("Port", required=True)
    serial_num = fields.Char("Serial Number", readonly=True)
    timeout = fields.Integer("Connection Timeout", default=10)
    cut_off_days = fields.Integer("Cut Off Days", default=3)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id)
    last_run_status = fields.Boolean("Last Run Status", default=False, readonly=1)
    last_error_msg = fields.Char("Last Error", readonly=True)

    def connect(self):
        """
        Connects and returns a connection object or exception if not connected
        @return: connection object, ZK object
        """
        zk, conn = None, None
        try:
            zk = ZK(self.machine_ip, port=self.port_num, timeout=self.timeout, ommit_ping=True)
            conn = zk.connect()
            self.last_run_status = True
            self.last_error_msg = None
            self.serial_num = conn.get_serialnumber()
        except Exception as ex:
            log.error(f"Failed to connect to: {self.name}[{self.machine_ip}:{self.port_num}]")
            self.last_run_status = False
            self.last_error_msg = str(ex)
        return conn, zk

    def test_connection(self):
        conn, zk = self.connect()
        res = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Connection status',
                'message': '',
                'sticky': False,
            }
        }
        if conn:
            conn.disconnect()
            res['params']['message'] = 'Connected successfully'
            res['params']['type'] = 'success'
        else:
            res['params']['message'] = 'Failed to connect'
            res['params']['type'] = 'danger'
        return res

    def get_attendances(self):
        for zk_machine in self:
            conn, zk = zk_machine.connect()
            if conn:
                start_date = datetime.now() - timedelta(days=zk_machine.cut_off_days)

                # Get the zk_attendances that are after the start date then sort it in timestamp asc order
                zk_attendances = list(filter(lambda attendance: attendance.timestamp > start_date, conn.get_attendance()))
                zk_attendances = sorted(zk_attendances, key=lambda a: a.timestamp)

                # Loop over the zk_attendances and for each zk_attendance, create a record in the zk.attendance.online model
                generated_attendances_ids = []
                for zk_attendance in zk_attendances:
                    log.info(f"Imported so far: {len(generated_attendances_ids)}")

                    # Check if there is an employee that already exists in the system with the same device ID
                    employee_id = self.env['hr.employee'].search([('device_id', '=', zk_attendance.user_id)])

                    # Set the original timezone to the employee if exists, else set it to the current user
                    original_timezone = tz.gettz(employee_id.tz) if employee_id and employee_id.tz else tz.gettz(self.env.user.tz)

                    # Convert the timestamp from the original time zone to utc timezone
                    utc_timezone = tz.gettz('UTC')
                    old_datetime = zk_attendance.timestamp.replace(tzinfo=original_timezone)
                    new_datetime = old_datetime.astimezone(utc_timezone).replace(tzinfo=None)

                    # Prevent duplicates in the log by making sure that the attendance we are trying to get does not exist
                    already_exists = self.env['zk.attendance.online'].search([
                        ('id_employee_device', '=', zk_attendance.user_id),
                        ('datetime', '=', new_datetime)
                    ])
                    if not already_exists:
                        generated_attendances_id = self.env['zk.attendance.online'].create({
                            'machine_id': zk_machine.id,
                            'id_employee_device': zk_attendance.user_id,
                            'datetime': new_datetime,
                        })
                        generated_attendances_ids.append(generated_attendances_id.id)
                        log.info(f"Employee ID: {zk_attendance.user_id} | Datetime {zk_attendance.timestamp} imported")
                    else:
                        log.info(f"Employee ID: {zk_attendance.user_id} | Datetime {zk_attendance.timestamp} already exist")

                if generated_attendances_ids:
                    generated_attendances = self.env['zk.attendance.online'].sudo().search([
                        ('id', 'in', generated_attendances_ids),
                        ('employee_id', '!=', False)
                    ])
                    generated_attendances.generate_zk_online_attendances()
