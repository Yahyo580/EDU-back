# Barcha sozlamalar shu yerda turadi. Kerak bo'lsa faqat shu faylni o'zgartiramiz.

import os

# Ustoz va adminlar shu token bilan kiradi.
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "8017758520")

# SQLite baza fayli. Railway/Volumes da doimiy saqlash uchun DB_PATH ni
# volume papkasiga ko'rsatish kifoya (masalan: /data/edu.db).
DB_PATH = os.environ.get("DB_PATH", "edu.db")

# Frontend qayerdan so'rov yuborishi mumkin.
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

# Telegram bot (Xabarlar / Aloqa bo'limi).
# TELEGRAM_BOT_TOKEN - BotFather'dan olingan token.
# TELEGRAM_CHAT_ID - xabarlar qayerga tushishi (botga /start bosilganda bot uni ko'rsatadi).
# Pastdagi qiymatlar - tayyor ishlab ketishi uchun. Xohlasangiz env orqali almashtiring.
TELEGRAM_BOT_TOKEN = os.environ.get(
    "TELEGRAM_BOT_TOKEN", "8937808137:AAFReoeLgcZBQQYD8c_yQhp9q230f2CnWqI"
)
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8017758520")

# Ism familiya uchun ruxsat etilgan belgilar (raqam yozib bo'lmaydi).
NAME_PATTERN = r"^[A-Za-zА-Яа-яЎўҚқҒғҲҳ'\u02bc` ]{3,60}$"

# Rasm juda katta bo'lib ketmasligi uchun chegara (base64 belgilarda ~4MB).
MAX_MEDIA_CHARS = 6_000_000
