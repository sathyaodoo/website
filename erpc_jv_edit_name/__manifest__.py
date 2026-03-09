{
    'name': 'ERPC JV EDIT NAME',
    'sequence': -102,
    'category': 'Accounting',
    'description': 'Restrict editing of JV name only for the specific group: Can Edit JV Name,',
    'summary': 'Restrict editing of JV name',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'depends': [
        'base', 'account', 'erpc_multi_edits',
    ],
    'data': [
        # 'security/group.xml',
        # 'views/account_move_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}