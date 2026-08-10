"""Kirish (login) bilan bog'liq yo'llar."""

from fastapi import APIRouter, HTTPException

from ..config import STAFF_TOKENS
from ..db import clean_row, conn
from ..models import LoginIn
from ..utils import check_name, now_text

router = APIRouter(prefix="/api", tags=["auth"])


def write_login(c, user):
    """Kim, qachon kirganini yozib qo'yamiz - admin buni ko'radi."""
    c.execute(
        "INSERT INTO logins(user_id, name, role, status, at) VALUES(?,?,?,?,?)",
        (user["id"], user["name"], user["role"], user["status"], now_text()),
    )


@router.post("/login")
def login(data: LoginIn):
    if data.role not in ("student", "teacher", "admin"):
        raise HTTPException(400, "Noto'g'ri rol")

    name = check_name(data.name)
    secret = (data.secret or "").strip()

    c = conn()
    user = c.execute("SELECT * FROM users WHERE name = ?", (name,)).fetchone()

    if data.role == "student":
        login_student(c, user, name, secret)
    else:
        login_staff(c, user, name, secret, data.role)

    c.commit()
    user = c.execute("SELECT * FROM users WHERE name = ?", (name,)).fetchone()
    write_login(c, user)
    c.commit()
    c.close()
    return clean_row(user)


WEAK_MSG = "Parol murakkab bo'lishi shart: kamida 8 ta belgi, ichida harf, raqam va belgi bo'lsin"


def weak_password(password: str) -> bool:
    """Parol murakkabligi: >=8 belgi, harf + raqam + belgi bo'lishi kerak."""
    if len(password) < 8:
        return True
    if not any(ch.isalpha() for ch in password):
        return True
    if not any(ch.isdigit() for ch in password):
        return True
    if not any(not ch.isalnum() for ch in password):
        return True
    return False


def login_student(c, user, name, password):
    """O'quvchi: ism + doimiy parol. Yangi parol murakkab bo'lishi shart."""
    if user is None:
        if weak_password(password):
            c.close()
            raise HTTPException(400, WEAK_MSG)
        c.execute(
            "INSERT INTO users(name, role, password, status) VALUES(?,?,?,?)",
            (name, "student", password, "viewer"),
        )
    elif not user["password"]:
        # Ustoz oldindan qo'shgan bo'lsa, birinchi kirish parolni belgilaydi.
        if weak_password(password):
            c.close()
            raise HTTPException(400, WEAK_MSG)
        c.execute("UPDATE users SET password=? WHERE id=?", (password, user["id"]))
    elif user["password"] != password:
        c.close()
        raise HTTPException(401, "Parol noto'g'ri")


def login_staff(c, user, name, token, role):
    """Ustoz va admin: ism + ruxsat etilgan token (whitelist)."""
    if token not in STAFF_TOKENS:
        c.close()
        raise HTTPException(401, "Token noto'g'ri")

    if user is None:
        c.execute(
            "INSERT INTO users(name, role, token, status) VALUES(?,?,?,?)",
            (name, role, token, "active"),
        )
    else:
        c.execute(
            "UPDATE users SET token=?, role=?, status='active' WHERE id=?",
            (token, role, user["id"]),
        )
