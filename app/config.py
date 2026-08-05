# Barcha sozlamalar shu yerda turadi. Kerak bo'lsa faqat shu faylni o'zgartiramiz.

# Ustoz va adminlar shu token bilan kiradi.
ACCESS_TOKEN = "8017758520"

# SQLite baza fayli (backend papkasi ichida paydo bo'ladi).
DB_PATH = "edu.db"

# Frontend qayerdan so'rov yuborishi mumkin.
ALLOWED_ORIGINS = ["*"]

# Ism familiya uchun ruxsat etilgan belgilar (raqam yozib bo'lmaydi).
NAME_PATTERN = r"^[A-Za-zА-Яа-яЎўҚқҒғҲҳ'\u02bc` ]{3,60}$"

# Rasm juda katta bo'lib ketmasligi uchun chegara (base64 belgilarda ~4MB).
MAX_MEDIA_CHARS = 6_000_000
