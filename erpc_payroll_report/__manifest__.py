{
    'name': 'Payslip Input Description Matching',
    'sequence': 10,
    'category': 'Human Resources/Payroll',
    'description': """
        This module enhances the payroll functionality by:
        - Adding a computed field to `hr.payslip.line` that matches input descriptions with payslip lines based on the input type name.
        - Displaying the matching input description in the payslip form view and payslip report.
    """,
    'summary': 'Enhance payroll with matching input descriptions for payslip lines.',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'views/views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
