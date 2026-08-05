"""Davomat: ustoz belgilaydi, o'quvchi ko'radi."""

from fastapi import APIRouter, HTTPException

from ..db import clean_row, conn
from ..models import MarkIn

router = APIRouter(prefix="/api/attendance", tags=["attendance"])

STATUSES = ("keldi", "kechikdi", "yo'q")


def day_map(c, date):
    rows = c.execute("SELECT * FROM attendance WHERE date=?", (date,)).fetchall()
    return {str(r["student_id"]): clean_row(r) for r in rows}


@router.get("")
def by_date(date: str):
    c = conn()
    out = day_map(c, date)
    c.close()
    return out


@router.post("")
def mark(data: MarkIn):
    if data.status not in STATUSES:
        raise HTTPException(400, "Noto'g'ri holat")

    c = conn()
    prev = c.execute(
        "SELECT coins FROM attendance WHERE date=? AND student_id=?",
        (data.date, data.student_id),
    ).fetchone()
    prev_coins = prev["coins"] if prev else 0

    c.execute(
        "INSERT INTO attendance(date, student_id, status, coins, by_name)"
        " VALUES(?,?,?,?,?)"
        " ON CONFLICT(date, student_id) DO UPDATE SET"
        " status=excluded.status, coins=excluded.coins, by_name=excluded.by_name",
        (data.date, data.student_id, data.status, data.coins, data.by),
    )
    # Coin balansini faqat farqiga o'zgartiramiz (ikki marta qo'shilib ketmasin).
    c.execute(
        "UPDATE users SET coins = MAX(0, coins + ?) WHERE id=?",
        (data.coins - prev_coins, data.student_id),
    )
    c.commit()
    out = day_map(c, data.date)
    c.close()
    return out


@router.get("/student/{uid}")
def for_student(uid: int):
    c = conn()
    rows = c.execute(
        "SELECT * FROM attendance WHERE student_id=? ORDER BY date DESC", (uid,)
    ).fetchall()
    c.close()
    return [clean_row(r) for r in rows]
