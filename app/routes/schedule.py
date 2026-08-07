"""Dars jadvali: ustoz/admin qo'shadi va o'chiradi, hamma ko'radi."""

from fastapi import APIRouter, HTTPException

from ..db import conn
from ..models import ScheduleIn

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

DAYS_ORDER = {
    "Dushanba": 1, "Seshanba": 2, "Chorshanba": 3,
    "Payshanba": 4, "Juma": 5, "Shanba": 6, "Yakshanba": 7,
}

ALL_DAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]


@router.get("")
def list_schedule(group: str = ""):
    c = conn()
    if group:
        rows = c.execute(
            "SELECT * FROM schedule WHERE \"group\"=? OR \"group\"='' ORDER BY id",
            (group,),
        ).fetchall()
    else:
        rows = c.execute("SELECT * FROM schedule ORDER BY id").fetchall()
    c.close()
    out = []
    for r in rows:
        d = dict(r)
        d["day_no"] = DAYS_ORDER.get(d["day"], 99)
        out.append(d)
    out.sort(key=lambda x: (x["day_no"], x["time"]))
    return out


@router.post("")
def add_lesson(data: ScheduleIn):
    day = (data.day or "").strip()
    subject = (data.subject or "").strip()
    if day not in DAYS_ORDER:
        raise HTTPException(400, "Noto'g'ri kun")
    if not subject:
        raise HTTPException(400, "Fan nomi bo'sh bo'lmasin")

    c = conn()
    c.execute(
        "INSERT INTO schedule(day, time, subject, \"group\", teacher, room)"
        " VALUES(?,?,?,?,?,?)",
        (day, data.time, subject, data.group, data.teacher, data.room),
    )
    c.commit()
    rows = c.execute("SELECT * FROM schedule ORDER BY id").fetchall()
    out = [dict(r) for r in rows]
    c.close()
    return out


@router.delete("/{sid}")
def delete_lesson(sid: int):
    c = conn()
    c.execute("DELETE FROM schedule WHERE id=?", (sid,))
    c.commit()
    rows = c.execute("SELECT * FROM schedule ORDER BY id").fetchall()
    out = [dict(r) for r in rows]
    c.close()
    return out
