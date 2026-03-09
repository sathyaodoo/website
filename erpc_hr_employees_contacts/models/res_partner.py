from odoo import models, fields, api

SYNC_FLAG = 'erpc_no_name_email_country_sync'


class ResPartner(models.Model):
    _inherit = "res.partner"

    erpc_employee_id = fields.Many2one(
        'hr.employee',
        string='Primary Employee',
        compute='_compute_erpc_employee_id',
        store=True,
        copy=False,
        compute_sudo=True,  # compute even if viewer isn't in HR
        readonly=False
    )
    employee_parent = fields.Boolean(copy=False)

    @api.depends('employee_ids', 'employee_ids.active')
    def _compute_erpc_employee_id(self):
        for partner in self:
            emps = partner.employee_ids
            # Prefer active; deterministic "first" by smallest id
            emp = emps.filtered('active').sorted('id')[:1] or emps.sorted('id')[:1]
            partner.erpc_employee_id = emp.id if emp else False

    # Master map: PARTNER FIELD -> EMPLOYEE FIELD
    _PARTNER_TO_EMP_MAP = {
        'name': 'name',
        'email': 'private_email',
        'mobile': 'private_phone',
        # 'phone': 'private_phone',
        'image_1920': 'image_1920',
        'street': 'private_street',
        'street2': 'private_street2',
        'city': 'private_city',
        'state_id': 'private_state_id',
        'zip': 'private_zip',
        'country_id': 'private_country_id',
        'birthdate': 'private_birthdate',
    }

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get(SYNC_FLAG):
            return res

        interesting = set(self._PARTNER_TO_EMP_MAP.keys()) | {'phone'}  # include phone for fallback to private_phone
        if interesting.intersection(vals.keys()):
            for partner in self:
                if partner.erpc_employee_id:
                    partner._sync_to_employee(vals_from_write=vals)
        return res

    def _sync_to_employee(self, vals_from_write=None):
        """Push changed fields from partner to linked employee without loops."""
        self.ensure_one()
        emp = self.erpc_employee_id
        if not emp:
            return

        updates = {}

        # If both 'mobile' and 'phone' were written, prefer 'mobile'
        phone_source = None
        if vals_from_write:
            if 'mobile' in vals_from_write:
                phone_source = 'mobile'
            elif 'phone' in vals_from_write:
                phone_source = 'phone'

        for partner_field, emp_field in self._PARTNER_TO_EMP_MAP.items():
            if partner_field == 'mobile':
                # handled via phone_source decision below
                continue

            if vals_from_write and partner_field not in vals_from_write:
                continue

            new_val = getattr(self, partner_field)

            if partner_field.endswith('_id') or emp_field.endswith('_id'):
                old_id = getattr(emp, emp_field).id if getattr(emp, emp_field) else False
                new_id = new_val.id if new_val else False
                if old_id != new_id:
                    updates[emp_field] = new_id or False
            else:
                if (emp[emp_field] or False) != (new_val or False):
                    updates[emp_field] = new_val or False

        # Phone/mobile → private_phone
        if phone_source:
            new_phone = getattr(self, phone_source) or False
            if emp.private_phone != new_phone:
                updates['private_phone'] = new_phone

        if updates:
            emp.with_context(**{SYNC_FLAG: True}).sudo().write(updates)

