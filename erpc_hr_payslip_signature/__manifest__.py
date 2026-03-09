{
    'name': 'HR - Payslip signature',
    'version': '19.0.1.0.0',
    'description': 'HR - Payslip signature',
    'category': 'HR - Payslip signature',
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': ['base', 'hr', 'hr_payroll', 'web', 'sign'],
    'application': True,
    'data': [
        'views/hr_payslip_view.xml',
        'views/template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'erpc_hr_payslip_signature/static/src/core/signature/signature_dialog.xml'
        ],
    },
    'license': 'OPL-1',
}