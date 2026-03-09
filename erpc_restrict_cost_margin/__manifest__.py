# -*- coding: utf-8 -*-
{
    'name': 'Restrict Cost & Margin',
    'version': '19.0.1.0.0',
    'summary': 'Restrict Cost & Margin',
    'category': 'sale',
    'description': """Restrict Cost & Margin""",
    'author': 'ERP Cloud SARL',
    'website': "https://www.erpcloudllc.com/",
    'license': 'LGPL-3',
    'depends': ['stock', 'sale', 'product', 'sale_margin', 'stock_account', 'hr_expense','product_margin'],
    'data': [
        'security/security.xml',
        # 'views/views.xml',
    ],
}
