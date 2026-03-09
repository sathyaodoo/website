from odoo import models, fields, api, _

SYNC_FLAG = 'erpc_no_name_email_country_sync'


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    private_birthdate = fields.Date(string="Private Birth Date")
    private_state_id = fields.Many2one(
        "res.country.state", string="Private State",
        domain="[('country_id', '=?', private_country_id)]",
        groups="hr.group_hr_user")

    # Master map: EMPLOYEE FIELD -> PARTNER FIELD
    _EMP_TO_PARTNER_MAP = {
        'name': 'name',
        'private_email': 'email',
        'private_phone': 'mobile',
        'private_street': 'street',
        'private_street2': 'street2',
        'private_city': 'city',
        'private_state_id': 'state_id',
        'private_zip': 'zip',
        'private_country_id': 'country_id',
        'private_birthdate': 'birthdate',
    }

    def _create_work_contacts(self):
        if any(employee.work_contact_id for employee in self):
            raise UserError(_('Some employee already have a work contact'))
        employee_parent_id = self.env['res.partner'].sudo().search([('employee_parent', '=', True)], limit=1)
        indoor_user_group = self.env.ref("erpc_hr_employees_contacts.group_is_indoor_user", raise_if_not_found=False)
        default_user = self.env["res.users"].search([("groups_id", "in", indoor_user_group.ids)],
                                                    limit=1) if indoor_user_group else False
        # customer_category_id = self.env["customer.category"].search([("employee_categ", "=", True)], limit=1)
        # business_id = self.env["business.type"].search([("employee_business_type", "=", True)], limit=1)
        work_contacts = self.env['res.partner'].create([{
            'email': employee.private_email,
            'mobile': employee.private_phone,
            'name': employee.name,
            'image_1920': employee.image_1920,
            'street': employee.private_street,
            'street2': employee.private_street2,
            'city': employee.private_city,
            'state_id': employee.private_state_id.id,
            'zip': employee.private_zip,
            'country_id': employee.private_country_id.id,
            'phone': employee.private_phone,
            'birthdate': employee.private_birthdate,
            'company_type': 'company',
            # 'collection_type': '0',
            # 'company_id': employee.company_id.id,
            'parent_id': employee_parent_id.id,
            'user_id': default_user.id,
            'property_payment_term_id': self.env.ref("account.account_payment_term_immediate").id,
            # 'customer_category_id': customer_category_id.id,
            # 'business_id': business_id.id,
            'property_account_receivable_id': self.env.company.company_receivable_account_id.id,
            'property_account_payable_id': self.env.company.company_payable_account_id.id,

        } for employee in self])
        for employee, work_contact in zip(self, work_contacts):
            employee.work_contact_id = work_contact

        # --- NEW: also assign AR/AP for MR on the SAME contact ---
        target_company = self.env['res.company'].browse(1)
        if target_company and target_company.exists():
            ar = target_company.company_receivable_account_id.id
            ap = target_company.company_payable_account_id.id

            # Write company-dependent properties in the context of company MR
            for partner in work_contacts.sudo():
                partner.with_company(target_company).write({
                    'property_account_receivable_id': ar,
                    'property_account_payable_id': ap,
                    'property_payment_term_id': self.env.ref("account.account_payment_term_immediate").id,
                })

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get(SYNC_FLAG):
            return res

        interesting = set(self._EMP_TO_PARTNER_MAP.keys())
        if interesting.intersection(vals.keys()):
            for emp in self:
                if emp.work_contact_id:
                    emp._sync_to_contact(vals_from_write=vals)
        return res

    def _sync_to_contact(self, vals_from_write=None):
        """Push changed fields from employee to linked partner without loops."""
        self.ensure_one()
        partner = self.work_contact_id
        if not partner:
            return

        updates = {}
        for emp_field, partner_field in self._EMP_TO_PARTNER_MAP.items():
            # Only consider fields that were actually written
            if vals_from_write and emp_field not in vals_from_write:
                continue

            new_val = getattr(self, emp_field)

            # M2O fields comparison by id
            if emp_field.endswith('_id') or partner_field.endswith('_id'):
                old_id = getattr(partner, partner_field).id if getattr(partner, partner_field) else False
                new_id = new_val.id if new_val else False
                if old_id != new_id:
                    updates[partner_field] = new_id or False

            # Scalar fields
            else:
                if (partner[partner_field] or False) != (new_val or False):
                    updates[partner_field] = new_val or False

        # mirror private_phone to partner.phone (secondary field)
        if 'private_phone' in (vals_from_write or {}) and partner.phone != (self.private_phone or False):
            updates.setdefault('phone', self.private_phone or False)

        if updates:
            partner.with_context(**{SYNC_FLAG: True}).sudo().write(updates)
