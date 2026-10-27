# -*- coding: utf-8 -*-
{
    'name': 'Password Manager Store',
    'version': '18.0.1.0.0',
    'summary': 'Centralized and secure credential storage for administrators',
    'description': """
Password Manager Store
======================
Store and manage all company credentials (social media, server logins,
third-party services) in one centralized, encrypted location inside Odoo.

Only authorized Password Store Administrators can access credentials.
All view and copy actions are recorded in a tamper-proof audit log.

Requirements:
- pip install cryptography
- Add password_store_key = <your-fernet-key> to odoo.conf
""",
    'category': 'Productivity',
    'author': 'Arif N Ramadhan',
    'website': 'https://www.niits.id',
    'support': 'sqlrif@gmail.com',
    'license': 'OPL-1',
    'price': 15.00,
    'currency': 'USD',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'views/account_views.xml',
        'views/access_log_views.xml',
        'views/category_views.xml',
        'views/menus.xml',
        'data/category_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'password_manager_store/static/src/copy_to_clipboard/copy_to_clipboard.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
