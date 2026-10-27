# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class PasswordStoreAccessLog(models.Model):
    _name = 'password.store.access.log'
    _description = 'Password Store Audit Log'
    _order = 'create_date desc'

    # Read-only — no write/unlink for anyone from UI
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        readonly=True,
        ondelete='restrict',
    )
    account_id = fields.Many2one(
        'password.store.account',
        string='Account',
        readonly=True,
        ondelete='set null',
    )
    account_name = fields.Char(
        string='Account Name',
        readonly=True,
        help='Stored separately so the log survives account deletion.',
    )
    action = fields.Selection(
        selection=[
            ('create', 'Create'),
            ('write', 'Write'),
            ('show', 'Show Password'),
            ('copy', 'Copy Password'),
            ('show_backup', 'Show Backup Codes'),
            ('copy_backup', 'Copy Backup Codes'),
            ('unlink', 'Delete'),
        ],
        string='Action',
        required=True,
        readonly=True,
    )
    ip_address = fields.Char(string='IP Address', readonly=True)

    # ------------------------------------------------------------------ #
    # Protect the log: no one can edit or delete entries via the ORM      #
    # ------------------------------------------------------------------ #
    def write(self, vals):
        raise AccessError(_("Audit log entries cannot be modified."))

    def unlink(self):
        raise AccessError(_("Audit log entries cannot be deleted."))

    # ------------------------------------------------------------------ #
    # Helper used by account.py                                           #
    # ------------------------------------------------------------------ #
    @api.model
    def _log(self, account, action):
        """Create an audit log entry. Call with sudo() from account methods."""
        request = self.env.get('request')
        ip = None
        try:
            from odoo.http import request as http_request
            if http_request and http_request.httprequest:
                ip = http_request.httprequest.remote_addr
        except Exception:
            pass

        self.sudo().create({
            'user_id': self.env.uid,
            'account_id': account.id if account else False,
            'account_name': account.name if account else False,
            'action': action,
            'ip_address': ip,
        })
