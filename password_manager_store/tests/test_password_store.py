# -*- coding: utf-8 -*-

from cryptography.fernet import Fernet

from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase, tagged
from odoo.addons.password_manager_store.models import crypto


@tagged('post_install', '-at_install', 'password_manager_store')
class TestPasswordManagerStore(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set a test fernet key
        cls.test_key = Fernet.generate_key().decode()
        cls.env['ir.config_parameter'].sudo().set_param('password_store_key', cls.test_key)

        cls.admin_group = cls.env.ref('password_manager_store.group_password_store_admin')
        cls.test_user = cls.env['res.users'].create({
            'name': 'Test Store User',
            'login': 'test_store_user',
            'email': 'test_store_user@example.com',
            'password': 'InitialSecretPassword123!',
        })

    def test_01_password_encrypted_on_create_and_write(self):
        """Verify password is encrypted with Fernet and audit log is created."""
        user = self.test_user
        self.assertTrue(user.has_stored_password)
        self.assertFalse(user.key_missing)
        self.assertTrue(user.password_encrypted.startswith('gAAAAA'))

        # Verify decryption
        plaintext = crypto.decrypt_value(self.env, user.password_encrypted)
        self.assertEqual(plaintext, 'InitialSecretPassword123!')

        # Verify update
        user.write({'password': 'UpdatedPassword456!'})
        updated_plaintext = crypto.decrypt_value(self.env, user.password_encrypted)
        self.assertEqual(updated_plaintext, 'UpdatedPassword456!')

    def test_02_show_and_copy_actions(self):
        """Verify show and copy password actions trigger audit logs."""
        user = self.test_user

        # Show password
        show_action = user.action_show_user_password()
        self.assertEqual(show_action['tag'], 'display_notification')
        self.assertEqual(show_action['params']['message'], 'InitialSecretPassword123!')

        # Copy password
        copy_action = user.action_copy_user_password()
        self.assertEqual(copy_action['tag'], 'password_manager_store.copy_to_clipboard')
        self.assertEqual(copy_action['params']['text'], 'InitialSecretPassword123!')

        # Check audit logs
        logs = self.env['password.store.access.log'].search([
            ('target_user_id', '=', user.id),
        ])
        actions = logs.mapped('action')
        self.assertIn('user_write', actions)
        self.assertIn('user_show', actions)
        self.assertIn('user_copy', actions)

    def test_03_audit_log_immutability(self):
        """Verify audit log entries cannot be modified or deleted."""
        user = self.test_user
        user.action_show_user_password()

        log = self.env['password.store.access.log'].search([
            ('target_user_id', '=', user.id),
        ], limit=1)

        with self.assertRaises(AccessError):
            log.write({'action': 'user_copy'})

        with self.assertRaises(AccessError):
            log.unlink()

    def test_04_wizard_set_password(self):
        """Verify wizard sets Odoo password and stores encrypted copy."""
        user = self.test_user

        wizard = self.env['password.store.set.user.password.wizard'].create({
            'user_id': user.id,
            'new_password': 'WizardSecret789!',
            'confirm_password': 'WizardSecret789!',
        })
        wizard.action_set_password()

        plaintext = crypto.decrypt_value(self.env, user.password_encrypted)
        self.assertEqual(plaintext, 'WizardSecret789!')

        # Wizard password mismatch validation
        with self.assertRaises(UserError):
            mismatch_wizard = self.env['password.store.set.user.password.wizard'].create({
                'user_id': user.id,
                'new_password': 'PasswordA',
                'confirm_password': 'PasswordB',
            })
            mismatch_wizard.action_set_password()

