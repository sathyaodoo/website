{
    'name': 'Sale - Quotation Restriction',
    'version': '19.0.1.0.0',
    'summary': 'Sale - Quotation Restriction',
    'description': """Sale - Quotation Restriction""",
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': ['base', 'sale'],
    'sequence': "-400",

    'data': [
        'security/security.xml',
    ],

    'application': True,
    'auto install': False,
    'license': 'LGPL-3',
}