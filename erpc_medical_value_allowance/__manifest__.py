{
    'name': 'ERP Cloud | Medical Value Allowance',
    'summary': 'ERP Cloud | Medical Value Allowance',
    'description': """ERP Cloud | Medical Value Allowance""",
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'author': 'ERP Cloud SARL',
    'website': "https://www.erpcloudllc.com/",
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'contacts', 'hr', 'erpc_hr_payroll_extension'],
    'data': [
        'security/ir.model.access.csv',
        'views/erpc_medical_value_allowance.xml',
    ],
    'application': True,
    'installable': True,
}
