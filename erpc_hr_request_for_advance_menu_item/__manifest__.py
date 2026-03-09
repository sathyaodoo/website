{
    'name': 'Request For Advance',
    'version': '19.0.1.0.0',
    'summary': 'Manage Request For Advance',
    'description': """
        Helps you to manage Advance Requests of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': [
        'base', 'hr_payroll', 'hr', 'account', 'erpc_hr_payroll_extension', 'spreadsheet_dashboard',
    ],
    'data': [
        # 'data/dashboards.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/request_for_advance_view.xml',
        'views/res_config_settings_view.xml',
        'views/account_move_view.xml',
        'wizard/reason_of_refusal_view.xml'
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
