# -*- coding: utf-8 -*-
{
    'name': 'Password Manager Store',
    'version': '19.0.5.0.0',
    'summary': 'View and manage Odoo user passwords securely — encrypted storage with audit trail',
    'description': """
Password Manager Store
======================
Allows Password Store Administrators to set, view, and copy Odoo user
passwords directly from the user form (Settings → Users → Password Store tab).

Passwords are stored encrypted using Fernet (AES-128-CBC) and every
reveal/copy action is recorded in a tamper-proof audit log.

Requirements:
- pip install cryptography
- Add password_store_key = <your-fernet-key> to odoo.conf
""",
    'category': 'Productivity',
    'author': 'Arif N Ramadhan',
    'website': 'https://www.niits.id',
    'support': 'sqlrif@gmail.com',
    'license': 'OPL-1',
    'price': 8.00,
    'currency': 'USD',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/set_user_password_wizard.xml',
        'views/access_log_views.xml',
        'views/res_users_views.xml',
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
