{
    'name': 'Email Reminder',
    'version': '19.0.1.0.0',
    'summary': 'Email Reminder',
    'description': """
        """,
    'category': 'Employee',
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': [
        'base', 'account','hr',
    ],
    'data': [
        'security/groups.xml',
        'views/view.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
