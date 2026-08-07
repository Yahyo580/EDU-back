"""Xabarlar bo'limi.

Foydalanuvchi saytdan xabar yuboradi -> backend bazaga saqlaydi va
Telegram bot orqali markazning chatiga yetkazadi (TELEGRAM_CHAT_ID).

Telegram'ga yuborish muvaffaqiyatsiz bo'lsa ham xabar bazada qoladi va
/status API orqali ko'rinadi - ilova ishdan chiqmaydi.
"""

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException

from ..config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from ..db import conn
from ..models import MessageIn
from ..utils import now_text

router = APIRouter(prefix="/api", tags=["messages"])


def _escape(s):
    """Telegram HTML parse_mode uchun belgilarni himoyalaymiz."""
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _telegram_send(chat_id, message):
    """Bot orqali xabarni belgilangan chatga yuboradi. Xato bo'lsa False qaytadi."""
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        body = urlencode({"chat_id": chat_id, "text": message, "parse_mode": "HTML"}).encode()
        with urlopen(Request(url, data=body, method="POST"), timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


@router.post("/messages")
def create_message(data: MessageIn):
    text = (data.text or "").strip()
    if not text:
        raise HTTPException(400, "Xabar matni bo'sh bo'lmasin")

    name = (data.name or "Anonim").strip()[:60]
    contact = (data.contact or "").strip()[:80]

    c = conn()
    c.execute(
        "INSERT INTO messages(name, contact, text, created_at) VALUES(?,?,?,?)",
        (name, contact, text, now_text()),
    )
    c.commit()
    c.close()

    message = (
        "<b>\U0001F4E9 EduCenter saytidan yangi xabar</b>\n"
        f"\U0001F464 {_escape(name)}\n"
        f"\U0001F4DE {_escape(contact) if contact else '—'}\n"
        f"\U0001F4AC {_escape(text)}"
    )
    sent = _telegram_send(TELEGRAM_CHAT_ID, message)
    return {"ok": True, "sent_to_telegram": sent}


@router.get("/messages")
def list_messages(limit: int = 100):
    c = conn()
    rows = c.execute("SELECT * FROM messages ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


@router.get("/telegram/bot")
def telegram_bot_info():
    """Bot haqida ochiq ma'lumot - frontend https://t.me/<username> havolasini quradi."""
    if not TELEGRAM_BOT_TOKEN:
        return {"available": False}
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        with urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        u = data.get("result", {})
        if data.get("ok"):
            return {
                "available": True,
                "username": u.get("username", ""),
                "name": u.get("first_name", ""),
            }
    except Exception:
        pass
    return {"available": False}
