from odoo import models, fields, api


class FamilyInfo(models.Model):
    _name = 'family.info'

    erpc_employee_id = fields.Many2one('hr.employee')

    erpc_type = fields.Selection(selection=[
        ('spouse', 'Spouse'),
        ('husband', 'Husband'),
        ('kid', 'Kid'),
    ], string='Type')
    erpc_name = fields.Char(string='Name')
    dob = fields.Date(string='DOB')
    dod = fields.Date(string='DOD')
    sex = fields.Selection(selection=[
        ('female', 'Female'),
        ('male', 'Male'),
    ], string='Sex')

    student = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="Student")
    college_uni = fields.Char(string='College/ Univ. Name')
    incapacity = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="Incapacity (Y/N)")
    family_status = fields.Selection(selection=[
        ('married', 'Married'),
        ('single', 'Single'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ], string='Family Status')
    dependant_on_employee = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="Dependant on Employee")
