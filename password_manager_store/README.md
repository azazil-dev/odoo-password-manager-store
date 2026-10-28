# Password Manager Store for Odoo 19

[![Odoo Version](https://img.shields.io/badge/Odoo-19.0-714B67.svg?style=flat-square)](https://www.odoo.com)
[![License](https://img.shields.io/badge/License-OPL--1-059669.svg?style=flat-square)](https://www.odoo.com/documentation/19.0/legal/licenses.html)
[![Price](https://img.shields.io/badge/Price-%2415%20USD-0284C7.svg?style=flat-square)](https://apps.odoo.com)
[![Security](https://img.shields.io/badge/Security-Fernet%20AES--128--CBC-DC2626.svg?style=flat-square)](https://cryptography.io/en/latest/fernet/)

**Store, view, and copy Odoo user passwords and external credentials — all encrypted, all audited.**

Manage company credentials in two ways:
- **User Passwords:** Automatically captures Odoo user passwords when set or changed by an administrator. Reveal or copy them later without resetting.
- **External Accounts:** Store social media, server root logins, database secrets, payment gateways, and third-party SaaS API credentials.

All access is restricted to authorized administrators with a tamper-proof audit trail for every reveal and copy action.

---

## 🌟 Key Highlights

- **🔒 Fernet Encryption at Rest:** Passwords and backup codes are encrypted using AES-128-CBC + HMAC-SHA256 via Python's standard `cryptography` library.
- **🛡 Zero-Leak Architecture:** Passwords are never stored in plaintext, never written to log files, excluded from tracking/chatter, and hidden from default exports.
- **🗝 Isolated Master Key:** The encryption key lives exclusively in `odoo.conf` (`password_store_key`), keeping secrets safe even if database backups are leaked or exposed.
- **📜 Tamper-Proof Audit Trail:** Every `reveal` (view password), `copy`, `create`, `write`, and `unlink` event records user ID, precise timestamp, and client IP address. Audit entries cannot be modified or deleted.
- **🏢 Multi-Company Isolation:** Multi-tenancy support ensures administrators only view and manage credentials belonging to their active company.
- **👥 Strict Role-Based Security (RBAC):** All menus, views, models, and JSON-RPC endpoints are hidden from standard users and locked to the *Password Store Administrator* group.
- **🏷 Smart Categorization & Tagging:** Organize accounts with predefined categories (Social Media, Server / Hosting, Payment Gateway, SaaS, Database, Internal) and custom tags.

---

## 📋 Compatibility

| Feature | Details |
|---|---|
| **Odoo Editions** | Odoo 19.0 Community Edition (CE) & Enterprise Edition (EE) |
| **Hosting Model** | On-Premise, Dedicated Server, Private Cloud (Docker / Kubernetes / VMs) |
| **Unsupported** | Odoo Online (SaaS) and Odoo.sh (requires direct write access to `odoo.conf`) |
| **Dependencies** | Odoo core modules `base`, `mail`, and Python library `cryptography` |

---

## 🚀 Installation & Quick Start

### 1. Install Prerequisites
Ensure the `cryptography` package is installed in your Odoo Python environment:
```bash
pip install cryptography
```
*(In Docker setups, add `cryptography>=41.0.0` to your container requirements).*

### 2. Generate Your Master Encryption Key
Run this Python one-liner to generate a secure URL-safe 32-byte base64-encoded key:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
*Example output:* `Ym82Nm9pU3hNVXJ5bTJ1c1FzV3U3Q1ZkVmZ3ZXRpZ28=`

### 3. Configure `odoo.conf`
Append the generated key to your Odoo configuration file (`/etc/odoo/odoo.conf`):
```ini
[options]
password_store_key = YOUR_GENERATED_KEY_HERE
```

> [!CAUTION]
> **CRITICAL SECURITY NOTICE:**
> The master key is required to decrypt all stored secrets.
> - Store this key securely outside of your database backup.
> - If lost, encrypted passwords and backup codes are **permanently unrecoverable**. There is no back door.

### 4. Install the Module
1. Restart your Odoo server or Docker container.
2. Log in as an Administrator and activate **Developer Mode**.
3. Go to **Apps → Update Apps List**.
4. Search for **Password Manager Store** (`password_manager_store`) and click **Install**.

### 5. Grant User Permissions
Navigate to **Settings → Users & Companies → Users**, select the authorized administrative user, and assign the **Password Store Administrator** access right.

---

## 🛠 Usage Overview

1. **Accessing the Vault:** Go to the main menu **Access to Accounts → Accounts**.
2. **Creating Credentials:** Click **New**, fill in the service name, login URL, username, and password. Add backup codes, recovery email, and phone numbers if applicable. Click **Save**.
3. **Revealing Passwords:** Click the eye / **Show** button to temporarily reveal the decrypted password. This triggers an immutable audit log entry.
4. **Copying Credentials:** Click **Copy** to copy the password directly to your clipboard. This is also tracked in the audit trail.
5. **Auditing Access:** Check **Access to Accounts → Audit Log** anytime to review who accessed or copied specific passwords, along with timestamps and IP records.

---

## 🔒 Stored Account Schema

| Field Name | Type | Stored in DB | Encrypted at Rest |
|---|---|---|---|
| **Account / Name** | Char | Yes | Plaintext (Searchable) |
| **Category** | Many2one | Yes | Plaintext |
| **Website / URL** | Char | Yes | Plaintext (Direct Link) |
| **Username / Login** | Char | Yes | Plaintext |
| **Password** | Char | Computed | **Yes (Fernet AES-128-CBC)** |
| **Recovery Email** | Char | Yes | Plaintext |
| **Recovery Phone** | Char | Yes | Plaintext |
| **Backup Codes** | Text | Computed | **Yes (Fernet AES-128-CBC)** |
| **Responsible Admin** | Many2one | Yes | Plaintext |
| **Tags** | Many2many | Yes | Plaintext |
| **Notes** | Text | Yes | Plaintext |

---

## 🤝 Support & Inquiries

- **Official Vendor:** NIITS Inovasi Teknologi ([www.niits.id](https://www.niits.id))
- **Author:** Arif N Ramadhan
- **Email Support:** [sqlrif@gmail.com](mailto:sqlrif@gmail.com)
- **Standard Support:** 90 days from the purchase date for deployment and configuration assistance.

---

## 📄 License

Published under the **Odoo Proprietary License v1.0 (OPL-1)**.  
Copyright © 2024 Arif N Ramadhan. All Rights Reserved.
