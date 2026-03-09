# -*- coding: utf-8 -*-
{
    'name': "Import Images via URL",
    'summary': "Allow specific users to import images via URL",
    'description': """
        This module adds a new security group that allows non-admin users
        to import images via URL in data imports.
    """,
    'author': "Your Name",
    'website': "https://yourwebsite.com",
    'category': 'Tools',
    'version': '19.0.1.0.0',
    'depends': ['base', 'base_import'],
    'data': [
        # 'security/security.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}