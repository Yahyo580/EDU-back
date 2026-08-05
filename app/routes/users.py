"""Foydalanuvchilar: ro'yxat, status, o'quvchi qo'shish, coin."""

from fastapi import APIRouter, HTTPException

from ..db import clean_row, conn
from ..models import CoinsIn, StatusIn, StudentIn
from ..utils import check_name

router = APIRouter(prefix="/api", tags=["users"])

STATUSES = ("viewer", "student", "active", "blocked")


@router.get("/users")
def list_users(role: str | None = None):
    c = conn()
    if role:
        rows = c.execute("SELECT * FROM users WHERE role=? ORDER BY name", (role,))
    else:
        rows = c.execute("SELECT * FROM users ORDER BY name")
    out = [clean_row(r) for r in rows]
    c.close()
    return out


@router.get("/users/{uid}")
def get_user(uid: int):
    """Bitta foydalanuvchi - status yangilanganini tekshirish uchun kerak."""
    c = conn()
    u = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    c.close()
    if u is None:
        raise HTTPException(404, "Foydalanuvchi topilmadi")
    return clean_row(u)


@router.post("/users/{uid}/status")
def set_status(uid: int, data: StatusIn):
    if data.status not in STATUSES:
        raise HTTPException(400, "Noto'g'ri status")
    c = conn()
    c.execute("UPDATE users SET status=? WHERE id=?", (data.status, uid))
    c.commit()
    c.close()
    return {"ok": True}


@router.delete("/users/{uid}")
def delete_user(uid: int):
    c = conn()
    c.execute("DELETE FROM users WHERE id=?", (uid,))
    c.execute("DELETE FROM attendance WHERE student_id=?", (uid,))
    c.commit()
    c.close()
    return {"ok": True}


@router.post("/students")
def save_student(data: StudentIn):
    """Ustoz yoki admin o'quvchi qo'shadi / ma'lumotini yangilaydi."""
    name = check_name(data.name)
    c = conn()
    found = c.execute("SELECT id FROM users WHERE name=?", (name,)).fetchone()

    values = (
        data.group, data.age, data.parents, data.parent_phone,
        data.phone, data.address,
    )
    if found:
        c.execute(
            'UPDATE users SET "group"=?, age=?, parents=?, parent_phone=?,'
            " phone=?, address=? WHERE id=?",
            values + (found["id"],),
        )
    else:
        c.execute(
            'INSERT INTO users(name, role, status, "group", age, parents,'
            " parent_phone, phone, address, added_by)"
            " VALUES(?,'student','student',?,?,?,?,?,?,?)",
            (name,) + values + (data.added_by,),
        )
    c.commit()
    c.close()
    return {"ok": True}


@router.post("/students/{uid}/coins")
def change_coins(uid: int, data: CoinsIn):
    c = conn()
    c.execute("UPDATE users SET coins = MAX(0, coins + ?) WHERE id=?", (data.delta, uid))
    c.commit()
    c.close()
    return {"ok": True}


@router.get("/logins")
def login_history(limit: int = 50):
    c = conn()
    rows = c.execute("SELECT * FROM logins ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


@router.get("/stats")
def stats():
    c = conn()
    one = lambda q: c.execute(q).fetchone()[0]
    out = {
        "students": one("SELECT COUNT(*) FROM users WHERE role='student'"),
        "teachers": one("SELECT COUNT(*) FROM users WHERE role='teacher'"),
        "posts": one("SELECT COUNT(*) FROM posts"),
        "coins": one("SELECT COALESCE(SUM(coins),0) FROM users"),
    }
    c.close()
    return out
