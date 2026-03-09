{
    'name': 'ERPC Cash Flow IN OUT Report',
    'sequence': -102,
    'category': 'Accounting',
    'description': """ Cash Flow IN OUT Report For Odoo 17,
     where we extract first and last sections from Odoo Cash Flow Report,
      Add new sections for customized filters from Vendor/customer payments for Cash IN and Cash OUT sections""" ,
    'summary': 'Cash Flow IN OUT Report For Odoo 17',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'depends': ['base', 'account', 'account_reports', 'yoko_customization' ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/customized_cash_flow_report.xml',
        # 'data/account_report_actions.xml',
        # 'data/menuitems.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,


}
