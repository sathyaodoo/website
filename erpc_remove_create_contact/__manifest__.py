{
    'name': 'ERPC Remove creation of contact',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'author': 'ERP Cloud S.A.R.L',
    'sequence': -100,
    'summary': 'ERPC Remove creation of contact',
    'description': """ ERPC Remove creation of contact """,
    'depends': ['base', 'account', 'stock', 'crm', 'website_crm_partner_assign'],
    'data': [
        'views/account_payment.xml',
        'views/crm_lead.xml',
        'views/stock_warehouse.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
