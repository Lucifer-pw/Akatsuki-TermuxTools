# ⚡ Akatsuki Termux Tools v2.0 (Modern Reborn)

Kumpulan tools utilitas Termux modern dengan arsitektur modular berstandar Python 3, antarmuka **TUI (Terminal User Interface)** yang rapi, serta mengusung estetika visual **Akatsuki (Awan Merah & Putih berbingkai hitam)**.

---

## 📸 Fitur Utama

1. **📱 OSINT Phone Intelligence Scanner**:
   - Validasi format ITU-T E.164 untuk semua nomor telepon internasional (`+62`, `+1`, `+44`, dsb.).
   - Deteksi operator seluler lokal/global (Telkomsel, Indosat, XL, Smartfren, Tri, AT&T, Verizon, dll.).
   - Deteksi tipe jaringan (*Mobile*, *Fixed Line*, *VoIP*), lokasi wilayah, dan zona waktu (Timezone).
   - Generator **OSINT Footprint & Search Dorks** untuk melacak akun tertaut di Instagram, TikTok, Facebook, Twitter/X, LinkedIn, WhatsApp, Telegram, serta dokumen dan pastebin publik.

2. **📡 Router Automation & Reboot**:
   - Pemindaian otomatis IP gateway router lokal (`192.168.1.1` atau `192.168.100.1`).
   - Database kredensial default router ISP di Indonesia (IndiHome ZTE `user`/`user1234`, ZTE Admin `admin`/`Telkomdso123`, Huawei ONT, TP-Link, generic).
   - Pengiriman instruksi reboot/restart terautentikasi langsung dari terminal tanpa perlu login manual via web browser.

3. **⚡ Network & Bandwidth Optimizer**:
   - **Benchmark Multi-DNS**: Menguji latensi query (ms) ke Cloudflare (1.1.1.1), Google (8.8.8.8), Quad9 (9.9.9.9), AdGuard DNS (94.140.14.14), dan merekomendasikan DNS tercepat beserta panduan Private DNS di Android.
   - **Ping Keep-Alive Daemon**: Mengirim probe ringan berkala untuk mencegah Android masuk ke WiFi sleep / power saving mode serta memantau latensi dan packet loss secara real-time.
   - **MTU Path Finder**: Menghitung ukuran MTU optimal tanpa fragmentasi (Don't Fragment flag).
   - **LAN Device Scanner (NetCut-Style)**: Memindai perangkat apa saja yang sedang aktif terhubung ke jaringan WiFi Anda lengkap dengan deteksi MAC, OUI vendor, dan deep identification untuk merk HP asli!
   - **Bandwidth Activity Monitor**: Menganalisis beban WiFi per perangkat secara real-time, mengidentifikasi aktivitas (Torrent/Download, Video Streaming, Browsing, Idle) dan mendeteksi tersangka utama penyebab WiFi lemot!

4. **🛡️ Network Security & Protection (BARU)**:
   - **Anti-NetCut Live Sentinel**: Mendeteksi serangan ARP spoofing / pemutusan koneksi secara real-time, menampilkan IP dan MAC penyerang.
   - **Static ARP Lock**: Mengunci pasangan IP-MAC gateway menjadi statis agar perangkat kebal 100% dari NetCut!
   - **Intruder / Rogue Device Alert**: Sistem Whitelist untuk memantau apakah ada HP/perangkat asing yang menyusup ke WiFi Anda.
   - **Nmap Security Auditor**: Memindai port dan celah keamanan router (Telnet, FTP, UPnP, TR-069) menggunakan Nmap asli atau Pure Python Fallback Scanner.

5. **🎨 Akatsuki TUI Dashboard & Auto-Update**:
   - Banner ASCII Awan Akatsuki berwarna merah dan putih kontras.
   - Navigasi angka interaktif (`[1]` s/d `[7]`) yang sangat nyaman ditekan pada keyboard virtual Android.
   - Fitur **Auto-Update**: Tarik kode dan pembaruan terbaru langsung dari GitHub (`git pull`) langsung dari dalam menu aplikasi!

---

## 🚀 Panduan Instalasi di Termux (Android)

Jalankan perintah berikut pada aplikasi Termux Anda:

```bash
# 1. Update dan install paket dasar
pkg update && pkg upgrade -y
pkg install python git -y

# 2. Clone repositori ini atau salin folder proyek
cd ~/
# (atau masuk ke direktori tempat proyek disimpan)
cd Akatsuki-TermuxTools

# 3. Install dependensi Python
pip install -r requirements.txt

# 4. Jalankan Akatsuki Tools!
python akatsuki.py
```

---

## 📂 Struktur Direktori

```
Akatsuki-TermuxTools/
├── akatsuki.py               # Entry-point utama & Dashboard TUI
├── requirements.txt          # Dependensi Python murni (Rich, phonenumbers, dnspython, dll.)
├── config.json               # Konfigurasi aktif (IP gateway, default credentials, dll.)
├── config.example.json       # Template konfigurasi awal
│
├── core/                     # Sistem Inti & Mesin TUI
│   ├── banner.py             # Banner ASCII Awan Akatsuki & header responsif
│   ├── theme.py              # Skema warna Akatsuki (Crimson Red, White, Dark Grey)
│   ├── menu.py               # Generator menu dan prompt interaktif
│   └── utils.py              # Deteksi gateway, IP lokal, status baterai & Termux
│
├── modules/                  # Modul Fungsional Mandiri
│   ├── osint_phone/          # Modul 1: Phone Intelligence & OSINT Dorks
│   ├── router_control/       # Modul 2: Router Automation & Drivers (ZTE, Huawei, TP-Link)
│   └── net_optimizer/        # Modul 3: DNS Benchmark, Ping Keep-Alive, MTU Finder
│
└── tests/                    # Pengujian Unit (Unit Testing)
    ├── test_osint.py
    ├── test_router.py
    └── test_network.py
```

---

## 🔒 Catatan Keamanan & Etika

- Fitur **OSINT Phone Intelligence** menggunakan engine resmi *Google Libphonenumber* dan generator pencarian dork publik. Tool ini **tidak melakukan brute-force atau scraping ilegal** pada form pemulihan akun pribadi.
- Fitur **Router Automation** ditujukan untuk mempermudah pemeliharaan router milik pribadi atau jaringan rumah resmi Anda.

---
*Dibuat dengan dedikasi untuk komunitas Termux & Akatsuki Theme.*
