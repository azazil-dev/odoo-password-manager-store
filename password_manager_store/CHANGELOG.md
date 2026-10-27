# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/) and Semantic Versioning (`17.0.MAJOR.MINOR.PATCH`).

## [17.0.1.0.0] - Initial Release (Planned)

### Added
- Menu **Access to Accounts** with submenus: **Accounts**, **Audit Log**, **Configuration**.
- Model `password.store.account` storing Username, Password, Recovery Email, Recovery Phone, and Backup/Access Codes.
- Fernet encryption (AES-128-CBC + HMAC) for password and backup codes, master key in `odoo.conf`.
- **Show** and **Copy** buttons on the account form.
- **Quick Search** by name, username, URL, recovery email, category, and tags.
- Category and tag master data, with seed categories.
- Audit log (create, write, show, copy, unlink) — read-only, tamper-proof.
- **Password Store Administrator** security group and multi-company record rules.
- Indonesian (`id`) and English (`en`) translations plus `.pot` template.
- `README.md` with full installation guide and key management instructions.

### Security
- Encrypted fields restricted to admin group; excluded from tracking, export, and search.
- Audit log entries cannot be edited or deleted via the ORM.

## [17.0.1.1.0] - Planned

### Added
- Chatter on accounts (without sensitive values), password generator, strength indicator.

## [17.0.1.2.0] - Planned

### Added
- Master key rotation (re-encrypt all), encrypted CSV import/export.
