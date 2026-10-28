# -*- coding: utf-8 -*-
"""
Wizard to set and store a user's password in one step.
Accessible from the Password Store tab on the user form.
"""

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..models import crypto


class SetUserPasswordWizard(models.TransientModel):
    _name = 'password.store.set.user.password.wizard'
    _description = 'Set & Store User Password'

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        readonly=True,
    )
    user_login = fields.Char(
        related='user_id.login',
        string='Login',
        readonly=True,
    )
    new_password = fields.Char(
        string='New Password',
        required=True,
    )
    confirm_password = fields.Char(
        string='Confirm Password',
        required=True,
    )

    def action_set_password(self):
        """Set the user's password and store an encrypted copy."""
        self.ensure_one()
        if self.new_password != self.confirm_password:
            raise UserError(_("Passwords do not match. Please try again."))
        if not self.new_password:
            raise UserError(_("Password cannot be empty."))

        # Set the actual Odoo password — this calls res.users.write()
        # which our override in res_users.py will intercept to store
        # the encrypted copy automatically.
        self.user_id.sudo().write({'password': self.new_password})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Password Updated'),
                'message': _(
                    "Password for %s has been set and stored securely.",
                    self.user_id.login,
                ),
                'type': 'success',
                'sticky': False,
            },
        }
