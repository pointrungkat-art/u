import requests
import time
import json
import random
from datetime import datetime

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def send_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [TG] {msg}")

def run():
    config = load_config()
    tg = config.get("telegram", {})
    token = tg.get("bot_token", "")
    groups = tg.get("groups", [])

    if not token or token == "ISI_TOKEN_BOT_DISINI":
        log("ERROR: Bot token belum diisi di config.json!")
        log("Ikuti SETUP.md untuk cara dapet token.")
        return

    if not groups:
        log("ERROR: Belum ada grup di config.json!")
        return

    log(f"Bot aktif! Memantau {len(groups)} grup.")
    last_sent = {}  # chat_id -> datetime

    while True:
        now = datetime.now()
        for group in groups:
            chat_id        = group.get("chat_id")
            message        = group.get("message", "")
            schedule_hours = group.get("schedule_hours", 6)
            gap_seconds    = group.get("gap_seconds", 45)

            if not chat_id or not message:
                continue

            last = last_sent.get(chat_id)
            elapsed = (now - last).total_seconds() if last else float("inf")

            if elapsed >= schedule_hours * 3600:
                log(f"Kirim ke {chat_id}...")
                result = send_message(token, chat_id, message)

                if result.get("ok"):
                    log(f"Berhasil kirim ke {chat_id}")
                    last_sent[chat_id] = now
                else:
                    log(f"Gagal ke {chat_id}: {result.get('description')}")

                # Gap acak antar grup biar lebih natural
                sleep_time = random.randint(
                    max(10, gap_seconds - 10),
                    gap_seconds + 15
                )
                log(f"Gap {sleep_time} detik sebelum grup berikutnya...")
                time.sleep(sleep_time)

        time.sleep(60)  # cek jadwal tiap 1 menit

if __name__ == "__main__":
    log("Telegram Promo Bot dimulai!")
    run()
