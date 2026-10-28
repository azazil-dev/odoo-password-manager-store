# -*- coding: utf-8 -*-
"""
Fernet encryption helpers for Password Manager Store.

The master key is read from odoo.conf (parameter: password_store_key).
If the key is absent the encrypt/decrypt calls raise UserError with a
clear configuration message — no plaintext ever leaks silently.
"""

import logging

from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Lazy-import so the module loads even when cryptography is not installed;
# the error only surfaces when the user actually tries to save/show a password.
try:
    from cryptography.fernet import Fernet, InvalidToken
    _CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    _CRYPTOGRAPHY_AVAILABLE = False
    _logger.warning(
        "Password Manager Store: 'cryptography' library not installed. "
        "Run: pip install cryptography"
    )


def _get_fernet(env):
    """Return a Fernet instance using the key from odoo.conf."""
    if not _CRYPTOGRAPHY_AVAILABLE:
        raise UserError(_(
            "The 'cryptography' library is required by Password Manager Store "
            "but is not installed.\n\n"
            "Please run:  pip install cryptography\n"
            "then restart Odoo."
        ))

    key = env['ir.config_parameter'].sudo().get_param('password_store_key')
    if not key:
        # Also try reading directly from the Odoo configuration file
        try:
            from odoo.tools import config as odoo_config
            key = odoo_config.get('password_store_key')
        except Exception:
            key = None

    if not key:
        raise UserError(_(
            "Password Manager Store: master key is not configured.\n\n"
            "Add the following line to your odoo.conf:\n\n"
            "    password_store_key = <your-fernet-key>\n\n"
            "Generate a key with:\n"
            "    python -c \"from cryptography.fernet import Fernet; "
            "print(Fernet.generate_key().decode())\"\n\n"
            "⚠ Keep this key separate from your database backup. "
            "Losing the key means passwords cannot be recovered."
        ))

    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception as exc:
        raise UserError(_(
            "Password Manager Store: the configured master key is invalid.\n"
            "Please regenerate it and update odoo.conf.\n\nDetails: %s"
        ) % str(exc)) from exc


def encrypt_value(env, plaintext):
    """Encrypt *plaintext* and return a UTF-8 token string."""
    if not plaintext:
        return False
    f = _get_fernet(env)
    token = f.encrypt(plaintext.encode('utf-8'))
    return token.decode('utf-8')


def decrypt_value(env, token):
    """Decrypt *token* and return the original plaintext."""
    if not token:
        return ''
    f = _get_fernet(env)
    try:
        if isinstance(token, str):
            token = token.encode('utf-8')
        return f.decrypt(token).decode('utf-8')
    except Exception:
        # InvalidToken or wrong key — return empty rather than a crash, but log it
        _logger.exception(
            "Password Manager Store: failed to decrypt a value. "
            "The master key may have changed."
        )
        return _('(decryption failed — master key may have changed)')
