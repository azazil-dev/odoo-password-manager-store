# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class PasswordStoreAccessLog(models.Model):
    _name = 'password.store.access.log'
    _description = 'Password Store Audit Log'
    _order = 'create_date desc'

    user_id = fields.Many2one(
        'res.users',
        string='Admin',
        required=True,
        readonly=True,
        ondelete='restrict',
    )
    target_user_id = fields.Many2one(
        'res.users',
        string='User',
        readonly=True,
        ondelete='set null',
        help='The user whose password was accessed.',
    )
    account_name = fields.Char(
        string='User Name',
        readonly=True,
        help='Stored separately so the log survives user deletion.',
    )
    action = fields.Selection(
        selection=[
            ('user_write', 'Set Password'),
            ('user_show', 'Show Password'),
            ('user_copy', 'Copy Password'),
        ],
        string='Action',
        required=True,
        readonly=True,
    )
    ip_address = fields.Char(string='IP Address', readonly=True)

    # ------------------------------------------------------------------ #
    # Protect the log                                                    #
    # ------------------------------------------------------------------ #
    def write(self, vals):
        raise AccessError(_("Audit log entries cannot be modified."))

    def unlink(self):
        raise AccessError(_("Audit log entries cannot be deleted."))

    # ------------------------------------------------------------------ #
    # Helper                                                             #
    # ------------------------------------------------------------------ #
    @api.model
    def _get_ip(self):
        ip = None
        try:
            from odoo.http import request as http_request
            if http_request and http_request.httprequest:
                ip = http_request.httprequest.remote_addr
        except Exception:
            pass
        return ip

    @api.model
    def _log_user_password(self, target_user, action):
        """Create an audit log entry for a user password action."""
        self.sudo().create({
            'user_id': self.env.uid,
            'target_user_id': target_user.id if target_user else False,
            'account_name': target_user.name if target_user else False,
            'action': action,
            'ip_address': self._get_ip(),
        })
