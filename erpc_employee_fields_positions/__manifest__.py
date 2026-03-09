{
    "name": "HR Employee Fields Positions",
    "summary": "HR Employee Fields Positions",
    "description": """""",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    'author': 'ERP Cloud SARL',
    'website': "https://www.erpcloudllc.com/",
    "depends": ['hr', 'erpc_contract_history', 'hr_payroll', 'contacts', 'erpc_attendance_machine', 'erpc_employee_clothes_size'],
    "data": [
        'security/ir.model.access.csv',
        'views/erpc_hr_employee_views.xml',
        'views/erpc_hr_payroll_employee_views.xml',
    ],
    "license": "LGPL-3",
}
