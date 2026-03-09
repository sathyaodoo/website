{
    'name': 'HR - Employees & Contacts',
    'version': '19.0.1.0.0',
    'summary': 'HR - Employees & Contacts',
    'description': """
        """,
    'category': 'Employee',
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': [
        'base',
        'hr',
        'account',
        # 'yoko_customization',
        # 'erpc_type_quotation',
    ],
    'data': [
        'security/security.xml',
        # 'views/customer_category.xml',
        # 'views/business_type.xml',
        'views/hr_employee.xml',
        'views/res_config_settings.xml',
        'views/res_partner.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
