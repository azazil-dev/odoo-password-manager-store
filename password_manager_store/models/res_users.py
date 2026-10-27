# -*- coding: utf-8 -*-
"""
Inherit res.users to capture password changes and store an encrypted copy.

When an administrator sets or changes a user's password, the plaintext
is encrypted (Fernet) and stored in ``password_encrypted``.  Administrators
with the *Password Store Administrator* group can later reveal or copy the
stored password without resetting it.
"""

from odoo import _, api, fields, models

from . import crypto


class ResUsers(models.Model):
    _inherit = 'res.users'

    # ------------------------------------------------------------------ #
    # Encrypted password copy (admin-only)                              #
    # ------------------------------------------------------------------ #
    password_encrypted = fields.Text(
        string='Encrypted Password',
        groups='password_manager_store.group_password_store_admin',
        copy=False,
    )
    has_stored_password = fields.Boolean(
        string='Password Stored',
        compute='_compute_has_stored_password',
    )
    key_missing = fields.Boolean(
        string='Master Key Missing',
        compute='_compute_key_missing',
    )

    # ------------------------------------------------------------------ #
    # Computed helpers                                                   #
    # ------------------------------------------------------------------ #
    @api.depends('password_encrypted')
    def _compute_has_stored_password(self):
        for rec in self:
            rec.has_stored_password = bool(rec.password_encrypted)

    def _compute_key_missing(self):
        for rec in self:
            try:
                crypto._get_fernet(self.env)
                rec.key_missing = False
            except Exception:
                rec.key_missing = True

    # ------------------------------------------------------------------ #
    # ORM overrides — capture plaintext before Odoo hashes it           #
    # ------------------------------------------------------------------ #
    @api.model_create_multi
    def create(self, vals_list):
        plaintexts = [vals.get('password') for vals in vals_list]
        records = super().create(vals_list)
        for rec, plaintext in zip(records, plaintexts):
            if plaintext:
                rec.password_encrypted = crypto.encrypt_value(self.env, plaintext)
                self.env['password.store.access.log']._log_user_password(
                    rec, 'user_write')
        return records

    def write(self, vals):
        plaintext = vals.get('password')
        result = super().write(vals)
        if plaintext:
            for rec in self:
                rec.password_encrypted = crypto.encrypt_value(
                    self.env, plaintext)
                self.env['password.store.access.log']._log_user_password(
                    rec, 'user_write')
        return result

    # ------------------------------------------------------------------ #
    # Action buttons                                                     #
    # ------------------------------------------------------------------ #
    def action_show_user_password(self):
        """Decrypt and display the user's password; log the action."""
        self.ensure_one()
        self.env['password.store.access.log']._log_user_password(
            self, 'user_show')
        plaintext = crypto.decrypt_value(self.env, self.password_encrypted)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Password for %s', self.login),
                'message': plaintext,
                'type': 'info',
                'sticky': True,
            },
        }

    def action_copy_user_password(self):
        """Copy the user's password to clipboard; log the action."""
        self.ensure_one()
        self.env['password.store.access.log']._log_user_password(
            self, 'user_copy')
        plaintext = crypto.decrypt_value(self.env, self.password_encrypted)
        return {
            'type': 'ir.actions.client',
            'tag': 'password_manager_store.copy_to_clipboard',
            'params': {
                'text': plaintext,
            },
        }
