# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from . import crypto


class PasswordStoreAccount(models.Model):
    _name = 'password.store.account'
    _description = 'Password Store Account'
    _inherit = ['mail.thread']
    _order = 'name'

    # ------------------------------------------------------------------ #
    # Basic fields                                                        #
    # ------------------------------------------------------------------ #
    name = fields.Char(
        string='Account / Service Name',
        required=True,
        tracking=True,
    )
    category_id = fields.Many2one(
        'password.store.category',
        string='Category',
        ondelete='set null',
        tracking=True,
    )
    url = fields.Char(string='Website / URL', tracking=True)
    username = fields.Char(string='Username', required=True, tracking=True)
    recovery_email = fields.Char(string='Recovery Email', tracking=True)
    recovery_phone = fields.Char(string='Recovery Phone', tracking=True)
    notes = fields.Html(string='Notes')
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
    tag_ids = fields.Many2many(
        'password.store.tag',
        string='Tags',
    )

    # ------------------------------------------------------------------ #
    # Encrypted storage fields (only readable by admin group)            #
    # ------------------------------------------------------------------ #
    password_encrypted = fields.Text(
        string='Encrypted Password',
        groups='password_manager_store.group_password_store_admin',
        copy=False,
    )
    backup_codes_encrypted = fields.Text(
        string='Encrypted Backup Codes',
        groups='password_manager_store.group_password_store_admin',
        copy=False,
    )

    # ------------------------------------------------------------------ #
    # Virtual (non-stored) computed fields for UI interaction            #
    # ------------------------------------------------------------------ #
    password = fields.Char(
        string='Password',
        compute='_compute_password',
        inverse='_inverse_password',
        groups='password_manager_store.group_password_store_admin',
        copy=False,
        store=False,
    )
    backup_codes = fields.Text(
        string='Backup / Access Codes',
        compute='_compute_backup_codes',
        inverse='_inverse_backup_codes',
        groups='password_manager_store.group_password_store_admin',
        copy=False,
        store=False,
    )

    # ------------------------------------------------------------------ #
    # Computed helpers                                                    #
    # ------------------------------------------------------------------ #
    @api.depends('password_encrypted')
    def _compute_password(self):
        for rec in self:
            if rec.password_encrypted:
                rec.password = crypto.decrypt_value(self.env, rec.password_encrypted)
            else:
                rec.password = False

    def _inverse_password(self):
        for rec in self:
            rec.password_encrypted = crypto.encrypt_value(self.env, rec.password)

    @api.depends('backup_codes_encrypted')
    def _compute_backup_codes(self):
        for rec in self:
            if rec.backup_codes_encrypted:
                rec.backup_codes = crypto.decrypt_value(self.env, rec.backup_codes_encrypted)
            else:
                rec.backup_codes = False

    def _inverse_backup_codes(self):
        for rec in self:
            rec.backup_codes_encrypted = crypto.encrypt_value(self.env, rec.backup_codes)

    # ------------------------------------------------------------------ #
    # Banner: warn if master key is not configured                       #
    # ------------------------------------------------------------------ #
    key_missing = fields.Boolean(
        string='Master Key Missing',
        compute='_compute_key_missing',
        store=False,
    )

    def _compute_key_missing(self):
        try:
            crypto._get_fernet(self.env)
            missing = False
        except Exception:
            missing = True
        for rec in self:
            rec.key_missing = missing

    # ------------------------------------------------------------------ #
    # Action buttons                                                      #
    # ------------------------------------------------------------------ #
    def action_show_password(self):
        """Decrypt and return the password for display; write to audit log."""
        self.ensure_one()
        self.env['password.store.access.log']._log(self, 'show')
        plaintext = crypto.decrypt_value(self.env, self.password_encrypted)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Password'),
                'message': plaintext,
                'type': 'info',
                'sticky': False,
            },
        }

    def action_copy_password(self):
        """Return the password to the client for clipboard copy; write to audit log."""
        self.ensure_one()
        self.env['password.store.access.log']._log(self, 'copy')
        plaintext = crypto.decrypt_value(self.env, self.password_encrypted)
        return {
            'type': 'ir.actions.client',
            'tag': 'password_manager_store.copy_to_clipboard',
            'params': {
                'text': plaintext,
            },
        }

    def action_show_backup_codes(self):
        """Decrypt and display backup codes; write to audit log."""
        self.ensure_one()
        self.env['password.store.access.log']._log(self, 'show_backup')
        plaintext = crypto.decrypt_value(self.env, self.backup_codes_encrypted)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Backup / Access Codes'),
                'message': plaintext,
                'type': 'info',
                'sticky': True,
            },
        }

    def action_copy_backup_codes(self):
        """Return the backup codes for clipboard copy; write to audit log."""
        self.ensure_one()
        self.env['password.store.access.log']._log(self, 'copy_backup')
        plaintext = crypto.decrypt_value(self.env, self.backup_codes_encrypted)
        return {
            'type': 'ir.actions.client',
            'tag': 'password_manager_store.copy_to_clipboard',
            'params': {
                'text': plaintext,
            },
        }

    # ------------------------------------------------------------------ #
    # ORM overrides — audit log                                          #
    # ------------------------------------------------------------------ #
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            self.env['password.store.access.log']._log(rec, 'create')
        return records

    def write(self, vals):
        # Remove password from tracking values before calling super so that
        # the chatter never contains any plaintext.
        vals.pop('password', None)
        vals.pop('backup_codes', None)
        result = super().write(vals)
        if any(k in vals for k in (
            'password_encrypted', 'backup_codes_encrypted',
            'username', 'url', 'recovery_email', 'recovery_phone',
        )):
            for rec in self:
                self.env['password.store.access.log']._log(rec, 'write')
        return result

    def unlink(self):
        for rec in self:
            self.env['password.store.access.log']._log(rec, 'unlink')
        return super().unlink()

    # ------------------------------------------------------------------ #
    # Prevent password from appearing in mail tracking                   #
    # ------------------------------------------------------------------ #
    def _track_template(self, changes):
        # Remove sensitive fields from tracking before they reach the chatter
        changes.discard('password_encrypted')
        changes.discard('backup_codes_encrypted')
        return super()._track_template(changes)
