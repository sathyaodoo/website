# -*- coding: utf-8 -*-
{
    'name': 'Cash Driver Template',
    'version': '19.0.1.0.0',
    'summary': 'Cash Driver Report',
    'sequence': -100,
    'description': """Cash Driver Report""",
    'depends': ['base', 'erpc_driver_collection'],
    'data': [
        'report/cash_driver_receipt.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
