{
    'name': 'Driver Collection',
    'version': '19.0.1.0.0',
    'summary': 'Driver Collection',
    'category': '',

    'description': """ Driver Collection """,
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': ['base', 'product', 'mail', 'account', 'yoko_customization'],
    'sequence': "-400",

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
    ],

    'application': True,
    'auto install': False,
    'license': 'LGPL-3',
}
