# PRD: Password Manager Store (Odoo 17)

**Author:** Arif N Ramadhan  |  **License:** OPL-1  |  **Versi target:** 17.0.1.0.0  |  **Status:** Draft

## 1. Ringkasan Produk

**Password Manager Store** adalah modul Odoo 17 untuk menyimpan dan mengelola seluruh kredensial akun (media sosial, login server, layanan pihak ketiga) di satu tempat terpusat di dalam Odoo. Modul menyimpan username, password, email pemulihan, dan kode akses/cadangan. Data hanya dapat dilihat oleh administrator yang berwenang, dan administrator **dapat melihat password** yang disimpan pengguna lain.

**Fitur unggulan**

- **Secure Storage**: password dan data sensitif disimpan di modul khusus, terenkripsi di database.
- **Recovery Info**: email pemulihan dan backup codes tersimpan aman.
- **Admin Access**: visibilitas dibatasi hanya untuk admin yang berwenang.
- **Quick Search**: pencarian cepat detail akun.

### Keputusan Produk Final

| Topik | Keputusan |
| --- | --- |
| Pembuat entri akun | Hanya Administrator Password Store; pengguna lain tidak memiliki akses sama sekali |
| Master key | Disimpan hanya di `odoo.conf` (`password_store_key`); tanpa fallback ke database |
| Platform | Hanya on-premise dan self-hosted. Odoo Online dan Odoo.sh tidak didukung karena modul membutuhkan akses ke `odoo.conf` untuk menyimpan master key |
| Dependensi `cryptography` | Dijelaskan di `README.md`, tidak dideklarasikan di manifest |
| Harga | USD 15 per modul, lisensi OPL-1 |
| Edisi | Odoo 17 Community dan Enterprise |
| Dukungan | 90 hari sejak pembelian lewat email sqlrif@gmail.com (website: www.niits.id). WhatsApp diberikan setelah pembelian saja |

## 2. Latar Belakang dan Masalah

Kredensial perusahaan sering tersebar di chat, spreadsheet, atau catatan pribadi. Akibatnya sulit dilacak, berisiko bocor, dan hilang saat karyawan keluar. Modul ini memusatkan kredensial pada sistem yang sudah dipakai perusahaan (Odoo) dengan kontrol akses dan jejak audit.

## 3. Tujuan dan Non-Tujuan

**Tujuan**

1. Menyediakan penyimpanan kredensial terpusat di dalam Odoo.
2. Membatasi akses hanya untuk administrator Password Store.
3. Password terenkripsi at-rest, tidak tersimpan plaintext di database.
4. Setiap melihat/menyalin password tercatat di audit log.
5. Pencarian dan filter cepat.

**Non-tujuan (di luar scope v1)**

- Auto-fill browser / ekstensi browser.
- Berbagi kredensial per-pengguna non-admin.
- Rotasi password otomatis ke layanan eksternal.
- Integrasi SSO / vault eksternal (HashiCorp Vault, dll.).

## 4. Persona dan Hak Akses

| Persona | Grup Odoo | Hak |
| --- | --- | --- |
| Password Store Administrator | `group_password_store_admin` | CRUD akun, lihat/salin password, lihat audit log, kelola kategori |
| Administrator Sistem | `base.group_system` (implied oleh grup di atas) | Sama dengan admin Password Store |
| Pengguna internal lain | Tidak ada | Menu tidak tampil, tidak ada akses model sama sekali |

Catatan: kebutuhan bahwa admin dapat melihat password pengguna berarti password harus **dienkripsi reversibel** (bukan hash satu arah).

## 5. Fitur dan Kebutuhan Fungsional

### 5.1 Manajemen Akun (Menu: Access to Accounts > Accounts)

**User story:** Sebagai admin, saya ingin membuat entri akun baru agar kredensial tersimpan terpusat.

**Field form akun**

| Field | Tipe | Wajib | Keterangan |
| --- | --- | --- | --- |
| Name | Char | Ya | Nama akun/layanan, misal Instagram Perusahaan |
| Category | Many2one | Tidak | Social Media, Server, Third-party, dll. |
| Website / URL | Char | Tidak | Alamat login atau host server |
| Username | Char | Ya | Username atau email login |
| Password | Char (terenkripsi) | Ya | Tampil sebagai titik-titik, ada tombol Show dan Copy |
| Recovery Email | Char | Tidak | Email pemulihan |
| Recovery Phone | Char | Tidak | Opsional |
| Backup / Access Codes | Text (terenkripsi) | Tidak | Kode cadangan, 2FA recovery |
| Notes | Html/Text | Tidak | Catatan tambahan |
| Responsible | Many2one res.users | Tidak | PIC akun |
| Company | Many2one | Ya | Multi-company |
| Active | Boolean | - | Untuk arsip |
| Tags | Many2many | Tidak | Label bebas |

**Acceptance criteria**

- Klik Create membuka form baru; Save menyimpan data dengan password terenkripsi.
- Password di list view tidak pernah ditampilkan.
- Tombol Show menampilkan password selama sesi form dan mencatat log.
- Tombol Copy menyalin ke clipboard dan mencatat log.
- Archive menyembunyikan akun tanpa menghapus.

### 5.2 Quick Search

- Search view mencari di: Name, Username, URL, Recovery Email, Tags, Category.
- Filter: Active, Archived, My Responsible, per Category.
- Group by: Category, Responsible, Company.
- **Password dan backup codes tidak dapat dicari** (terenkripsi dan tidak diindeks).

### 5.3 Kategori dan Tag

- Master data kategori (Configuration > Categories) dan tag, dikelola admin.
- Data demo/awal: Social Media, Server, Email, Third-party Service.

### 5.4 Audit Log

- Mencatat: user, akun, aksi (create, write, show, copy, unlink), waktu, dan IP bila tersedia.
- Read-only; tidak dapat diedit atau dihapus dari UI, termasuk oleh admin.
- Menu: Access to Accounts > Audit Log.

### 5.5 Notifikasi Keamanan (opsional v1.1)

- Chatter/mail.thread pada akun untuk riwayat perubahan non-sensitif.
- Nilai password **tidak pernah** ditulis ke chatter atau tracking.

## 6. Model Data

| Model | Deskripsi |
| --- | --- |
| `password.store.account` | Entri akun/kredensial utama |
| `password.store.category` | Kategori akun |
| `password.store.tag` | Tag akun |
| `password.store.access.log` | Audit log akses |

**Rancangan `password.store.account`**

- `password_encrypted` (Text, groups terbatas, `copy=False`): hasil enkripsi.
- `password` (Char, computed + inverse, tidak disimpan): getter mendekripsi, setter mengenkripsi.
- `backup_codes_encrypted` dan `backup_codes`: pola yang sama.
- Method: `action_show_password()`, `action_copy_password()` yang menulis ke access log.
- `_sql_constraints`: tidak ada unique pada username (satu username bisa dipakai di banyak layanan).

## 7. Keamanan (Prioritas Tertinggi)

1. **Enkripsi at-rest:** Fernet (AES-128-CBC + HMAC) dari library `cryptography`. Instalasi library dijelaskan di README.md dan tidak dideklarasikan di manifest.
2. **Manajemen kunci:** master key disimpan di `odoo.conf` (parameter `password_store_key`), **bukan** di database. Bila key tidak ada, modul menolak menyimpan/menampilkan password dan menampilkan pesan konfigurasi jelas.
3. **Access control:** `ir.model.access.csv` hanya memberi akses ke grup admin Password Store; tanpa baris akses untuk `base.group_user`.
4. **Record rules:** pembatasan per company (multi-company).
5. **Field-level groups:** field password hanya dapat dibaca grup admin, termasuk lewat RPC/API.
6. **Tanpa kebocoran:** password tidak masuk tracking chatter, log server, atau export default; ekspor field sensitif dinonaktifkan.
7. **Sudo terkontrol:** tidak menggunakan `sudo()` untuk membuka password di luar method resmi.
8. **Transport:** wajib HTTPS (dokumentasi deployment).
9. **Backup:** database backup dan master key harus disimpan terpisah; kehilangan key berarti password tidak dapat dipulihkan (ditulis di README).

## 8. UI/UX

**Struktur menu**

- **Access to Accounts** (menu utama, hanya grup admin)
  - **Accounts** (list, form, kanban opsional)
  - **Audit Log**
  - **Configuration** > Categories, Tags

**Alur utama:** Access to Accounts > Accounts > Create > isi Username, Password, Recovery information > Save.

**Detail UI (Odoo 17)**

- Widget `password` untuk input; tombol Show/Copy di samping field.
- Gunakan sintaks Odoo 17 (`invisible="..."` langsung, bukan `attrs`).
- List view: Name, Category, Username, URL, Responsible. Tanpa kolom password.
- Peringatan banner jika master key belum dikonfigurasi.

## 9. Kebutuhan Non-Fungsional

- **Kompatibilitas:** Odoo 17.0 Community dan Enterprise, untuk instalasi on-premise/self-hosted. Odoo Online dan Odoo.sh tidak didukung karena master key disimpan di odoo.conf yang hanya dapat diakses pada instalasi sendiri.
- **Performa:** list view 10.000 akun dimuat < 2 detik; dekripsi hanya saat form dibuka atau Show diklik.
- **Lokalisasi:** string dapat diterjemahkan (file `.pot`), disediakan `id.po` dan `en.po`.
- **Maintainability:** mengikuti pedoman OCA/Odoo, lint `pylint-odoo` lolos.
- **Multi-company:** didukung.

## 10. Struktur Modul

```
password_manager_store/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── account.py
│   ├── category.py
│   ├── tag.py
│   ├── access_log.py
│   └── crypto.py
├── security/
│   ├── security.xml
│   ├── ir.model.access.csv
│   └── rules.xml
├── views/
│   ├── account_views.xml
│   ├── access_log_views.xml
│   ├── category_views.xml
│   └── menus.xml
├── data/category_data.xml
├── i18n/ (id.po, en.po)
├── static/description/ (icon.png, index.html)
├── tests/
├── CHANGELOG.md
└── README.md
```

**Manifest (rancangan)**

```python
{
    'name': 'Password Manager Store',
    'version': '17.0.1.0.0',
    'summary': 'Centralized and secure credential storage for administrators',
    'category': 'Productivity',
    'author': 'Arif N Ramadhan',
    'website': 'https://www.niits.id',
    'support': 'sqlrif@gmail.com',
    'license': 'OPL-1',
    'price': 15.00,
    'currency': 'USD',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'views/account_views.xml',
        'views/access_log_views.xml',
        'views/category_views.xml',
        'views/menus.xml',
        'data/category_data.xml',
    ],
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
}
```

Catatan: modul dijual seharga USD 15 dengan lisensi OPL-1, sehingga `price` dan `currency` wajib ada di manifest. `external_dependencies` sengaja tidak dipakai; kebutuhan library `cryptography` dijelaskan di `README.md`, dan kode melakukan import dengan pesan error yang jelas bila library belum terpasang.

## 11. Rencana Pengujian

| ID | Skenario | Hasil yang diharapkan |
| --- | --- | --- |
| T1 | Admin membuat akun baru | Tersimpan, password di DB terenkripsi |
| T2 | Pengguna non-admin membuka menu atau memanggil RPC | Ditolak (AccessError) |
| T3 | Admin klik Show | Password tampil, log tercatat |
| T4 | Admin klik Copy | Clipboard terisi, log tercatat |
| T5 | Pencarian berdasarkan username/URL | Hasil sesuai |
| T6 | Pencarian berdasarkan isi password | Tidak ada hasil |
| T7 | master key hilang di odoo.conf | Pesan error konfigurasi, tidak ada data bocor |
| T8 | Edit password lalu cek chatter | Nilai password tidak muncul |
| T9 | Arsipkan lalu pulihkan akun | Berfungsi normal |
| T10 | Multi-company | Admin hanya melihat akun company aktif |

## 12. Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
| --- | --- | --- |
| Master key bocor atau hilang | Semua password terbuka atau tidak bisa dibuka | Simpan di luar DB, backup terpisah, dokumentasi prosedur |
| Admin menyalahgunakan akses | Kebocoran kredensial | Audit log tidak dapat dihapus, batasi jumlah admin |
| Backup DB dibawa pihak lain | Password tetap terenkripsi | Key terpisah dari DB |
| Rotasi key | Data lama tidak terbaca | Fitur re-encrypt di roadmap v1.2 |

## 13. Roadmap

- **v1.0:** CRUD akun, enkripsi, ACL, search, audit log, kategori dan tag.
- **v1.1:** Chatter, password generator, indikator kekuatan password.
- **v1.2:** Rotasi master key (re-encrypt), import/export CSV terenkripsi.
- **v2.0:** Berbagi akun ke pengguna/grup tertentu, notifikasi akses.

## 14. Kriteria Penerimaan Rilis v1.0

- Seluruh test T1 sampai T10 lulus.
- Tidak ada password plaintext di tabel database mana pun.
- Dokumentasi README dan panduan penggunaan lengkap.
- Modul terpasang dan di-upgrade tanpa error pada Odoo 17.0 bersih.

## 15. Changelog

Format mengikuti Keep a Changelog dan Semantic Versioning (`17.0.MAJOR.MINOR.PATCH`).

### &#91;17.0.1.0.0\] - Rilis Awal (Rencana)

**Added**

- Menu **Access to Accounts** dengan submenu **Accounts**, **Audit Log**, dan **Configuration**.
- Model `password.store.account` untuk menyimpan Username, Password, Recovery Email, Recovery Phone, dan Backup/Access Codes.
- Enkripsi password dan backup codes menggunakan Fernet dengan master key di `odoo.conf`.
- Tombol **Show** dan **Copy** password pada form akun.
- **Quick Search** berdasarkan nama, username, URL, recovery email, kategori, dan tag.
- Kategori dan tag akun, beserta data awal kategori.
- Audit log akses (create, write, show, copy, unlink) yang bersifat read-only.
- Grup keamanan **Password Store Administrator** dan record rules multi-company.
- Terjemahan Bahasa Indonesia dan Inggris, serta README.md berisi panduan instalasi library cryptography dan pengaturan master key.

**Security**

- Field password dibatasi untuk grup administrator dan tidak ikut tracking, export, maupun pencarian.

### &#91;17.0.1.1.0\] - Direncanakan

**Added**

- Chatter pada akun (tanpa nilai sensitif), password generator, indikator kekuatan password.

### &#91;17.0.1.2.0\] - Direncanakan

**Added**

- Rotasi master key (re-encrypt), import/export CSV terenkripsi.

## 16. Kesiapan Odoo Apps

Harga jual USD 15. Checklist sebelum submit:

- [ ] Nama teknis modul unik: `password_manager_store`
- [ ] `static/description/icon.png`, `banner.png`, screenshot, dan `index.html` untuk halaman toko
- [ ] Manifest berisi `price`, `currency`, `website`, `support`, dan `images`
- [ ] `README.md`: instalasi `pip install cryptography`, cara membuat dan menaruh `password_store_key` di `odoo.conf`, serta peringatan bahwa kehilangan key membuat password tidak bisa dipulihkan
- [ ] Pengujian di Odoo 17 Community dan Enterprise
- [ ] Disclaimer tanggung jawab di dokumentasi
- [ ] Kebijakan dukungan: 90 hari sejak pembelian lewat email sqlrif@gmail.com; nomor WhatsApp hanya diberikan setelah pembelian dan tidak dicantumkan di manifest, README, atau halaman toko
- [ ] Lolos `pylint-odoo`

---

*Author: Arif N Ramadhan | License: OPL-1*
