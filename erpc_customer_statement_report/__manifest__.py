# -*- coding: utf-8 -*-
{
    'name': "Customer Statement Report",

    'summary': """Customer Statement Report""",

    'description': """
        Customer Statement Report, Partner Ledger in foreign Currency
    """,
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'category': 'Accounting',
    'version': '19.0.1.0.0',
    'sequence': -100,
    'depends': ['base', 'sale','report_xlsx'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'report/customer_statement_report_view_xlsx.xml',
        # 'report/customer_statement_report_view_pdf.xml',
        # 'wizard/customer_statement_report_wizard.xml',

    ],
    'application': True,
    'installation': True,
    'auto_install': False,
}
