"""Topshiriqlar: ustoz qo'shadi, o'quvchi "bajardim" deb belgilaydi."""

from fastapi import APIRouter, HTTPException

from ..db import conn
from ..models import HomeworkIn, SubmitIn
from ..utils import now_text

router = APIRouter(prefix="/api/homeworks", tags=["homework"])


def with_meta(c, rows, stu=0):
    """Har bir topshiriq uchun bajardilar soni va (agar o'quvchi korsa) o'zi bajardimi."""
    total = c.execute(
        "SELECT COUNT(*) FROM users WHERE role='student' AND status='student'"
    ).fetchone()[0]
    out = []
    for r in rows:
        d = dict(r)
        d["done_count"] = c.execute(
            "SELECT COUNT(*) FROM submissions WHERE homework_id=?", (d["id"],)
        ).fetchone()[0]
        d["total_count"] = total
        if stu:
            d["done"] = c.execute(
                "SELECT 1 FROM submissions WHERE homework_id=? AND student_id=?",
                (d["id"], stu),
            ).fetchone() is not None
        else:
            d["done"] = False
            d["done_by"] = [
                r["student_name"]
                for r in c.execute(
                    "SELECT student_name FROM submissions WHERE homework_id=? ORDER BY id",
                    (d["id"],),
                )
            ]
        out.append(d)
    return out


@router.get("")
def list_homeworks(stu: int = 0):
    c = conn()
    rows = c.execute("SELECT * FROM homeworks ORDER BY id DESC").fetchall()
    out = with_meta(c, rows, stu)
    c.close()
    return out


@router.post("")
def create_homework(data: HomeworkIn):
    title = (data.title or "").strip()
    if not title:
        raise HTTPException(400, "Topshiriq nomi bo'sh bo'lmasin")

    c = conn()
    c.execute(
        "INSERT INTO homeworks(title, \"group\", subject, text, deadline, author, created_at)"
        " VALUES(?,?,?,?,?,?,?)",
        (
            title,
            data.group,
            data.subject,
            data.text,
            data.deadline,
            data.author,
            now_text(),
        ),
    )
    c.commit()
    rows = c.execute("SELECT * FROM homeworks ORDER BY id DESC").fetchall()
    out = with_meta(c, rows)
    c.close()
    return out


@router.delete("/{hid}")
def delete_homework(hid: int, by_name: str = ""):
    c = conn()
    hw = c.execute("SELECT * FROM homeworks WHERE id=?", (hid,)).fetchone()
    if hw is None:
        c.close()
        raise HTTPException(404, "Topshiriq topilmadi")
    if hw["author"] != by_name:
        c.close()
        raise HTTPException(403, "Faqat o'z topshirig'ingizni o'chira olasiz")
    c.execute("DELETE FROM homeworks WHERE id=?", (hid,))
    c.execute("DELETE FROM submissions WHERE homework_id=?", (hid,))
    c.commit()
    rows = c.execute("SELECT * FROM homeworks ORDER BY id DESC").fetchall()
    out = with_meta(c, rows)
    c.close()
    return out


@router.post("/{hid}/submit")
def submit(hid: int, data: SubmitIn):
    """O'quvchi topshiriqni bajardi/bajarganini bekor qildi."""
    c = conn()
    hw = c.execute("SELECT * FROM homeworks WHERE id=?", (hid,)).fetchone()
    if hw is None:
        c.close()
        raise HTTPException(404, "Topshiriq topilmadi")

    if data.done:
        c.execute(
            "INSERT INTO submissions(homework_id, student_id, student_name, submitted_at)"
            " VALUES(?,?,?,?)"
            " ON CONFLICT(homework_id, student_id) DO UPDATE SET"
            " student_name=excluded.student_name, submitted_at=excluded.submitted_at",
            (hid, data.student_id, data.student_name, now_text()),
        )
    else:
        c.execute(
            "DELETE FROM submissions WHERE homework_id=? AND student_id=?",
            (hid, data.student_id),
        )
    c.commit()
    c.close()
    return {"ok": True}
