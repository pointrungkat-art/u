# Setup Promo Bot

## Yang Dibutuhin
- Python 3.8+ (untuk Telegram)
- Node.js 18+ (untuk WhatsApp)
- Koneksi internet

---

## TELEGRAM SETUP

### Step 1 — Buat Bot Telegram
1. Buka Telegram, cari `@BotFather`
2. Ketik `/newbot`
3. Kasih nama bot (bebas)
4. Kasih username bot (harus diakhiri `bot`, contoh: `PromoKuBot`)
5. BotFather kasih **TOKEN** — copy token itu

### Step 2 — Isi Config
Buka `config.json`, ganti:
```
"bot_token": "ISI_TOKEN_BOT_DISINI"
```
Jadi:
```
"bot_token": "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"
```

### Step 3 — Tambahin Bot ke Grup
1. Buka grup Telegram tujuan
2. Klik nama grup → Edit → Tambah anggota
3. Cari username bot lo
4. Jadikan **Admin** (minimal bisa kirim pesan)

### Step 4 — Dapetin Chat ID Grup
**Cara 1 (username publik):**
Langsung pakai `@username_grup` di config.

**Cara 2 (grup private):**
1. Tambahkan `@userinfobot` ke grup
2. Ketik `/start` → bot kasih ID angka (contoh: `-1001234567890`)
3. Keluarkan bot itu setelah dapat ID

### Step 5 — Install & Jalankan
```bash
pip install -r requirements.txt
python telegram_sender.py
```

---

## WHATSAPP SETUP

### Step 1 — Install Dependencies
```bash
npm install
```

### Step 2 — Dapetin JID Grup
Jalankan sekali:
```bash
node wa_list_groups.js
```
Scan QR code pakai WA lo → nanti muncul daftar semua grup beserta JID-nya.
Copy JID yang mau ditarget.

### Step 3 — Isi Config
Buka `config.json`, ganti:
```
"jid": "ISI_JID_GRUP_DARI_wa_list_groups"
```
Jadi (contoh):
```
"jid": "120363012345678901@g.us"
```

### Step 4 — Jalankan Bot
```bash
node wa_sender.js
```
Scan QR pakai WA → bot aktif dan mulai kirim sesuai jadwal.

> Catatan: Sesi WA tersimpan di folder `wa_session/`.
> Kalau mau ganti nomor, hapus folder itu lalu restart.

---

## CARA EDIT PESAN & JADWAL

Semua ada di `config.json`:

| Field | Keterangan |
|---|---|
| `message` | Isi pesan yang dikirim ke grup itu |
| `schedule_hours` | Kirim ulang tiap berapa jam |
| `gap_seconds` | Jeda antar grup (detik) |

Contoh:
```json
{
  "chat_id": "@gruppromoku",
  "message": "Promo hari ini! Cek sekarang 🔥",
  "schedule_hours": 6,
  "gap_seconds": 45
}
```

## JALANKAN KEDUANYA SEKALIGUS

Buka 2 terminal:
```bash
# Terminal 1
python telegram_sender.py

# Terminal 2
node wa_sender.js
```

Atau pakai screen/tmux biar jalan di background:
```bash
screen -S telegram
python telegram_sender.py
# Ctrl+A lalu D untuk detach

screen -S whatsapp
node wa_sender.js
# Ctrl+A lalu D untuk detach
```
