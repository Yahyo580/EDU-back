"""Foydalanuvchilar: ro'yxat, status, o'quvchi qo'shish, coin, avatar."""

from fastapi import APIRouter, HTTPException

from ..config import MAX_MEDIA_CHARS
from ..db import clean_row, conn
from ..models import AvatarIn, CoinsIn, ProfileIn, StatusIn, StudentIn
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
    c.execute("DELETE FROM submissions WHERE student_id=?", (uid,))
    c.commit()
    c.close()
    return {"ok": True}


@router.delete("/groups/{group}")
def delete_group(group: str):
    """Guruhdagi barcha o'quvchilarni (davomat va topshiriqlari bilan) o'chiradi."""
    if not group.strip():
        raise HTTPException(400, "Guruh nomi bo'sh bo'lishi mumkin emas")
    c = conn()
    ids = [
        r["id"]
        for r in c.execute('SELECT id FROM users WHERE role="student" AND "group"=?', (group,))
    ]
    if not ids:
        c.close()
        raise HTTPException(404, "Bunday guruh topilmadi")
    q = ",".join("?" * len(ids))
    c.execute(f'DELETE FROM users WHERE id IN ({q})', ids)
    c.execute(f'DELETE FROM attendance WHERE student_id IN ({q})', ids)
    c.execute(f'DELETE FROM submissions WHERE student_id IN ({q})', ids)
    c.commit()
    c.close()
    return {"ok": True, "deleted": len(ids)}


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


@router.post("/users/{uid}/avatar")
def set_avatar(uid: int, data: AvatarIn):
    """Profil rasmi (data URL) o'rnatadi. Hammadan bir xil chegarada tekshiramiz."""
    avatar = (data.avatar or "").strip()
    if avatar and not avatar.startswith("data:image/"):
        raise HTTPException(400, "Rasm formati noto'g'ri")
    if len(avatar) > MAX_MEDIA_CHARS:
        raise HTTPException(400, "Rasm juda katta")

    c = conn()
    u = c.execute("SELECT id FROM users WHERE id=?", (uid,)).fetchone()
    if u is None:
        c.close()
        raise HTTPException(404, "Foydalanuvchi topilmadi")
    c.execute("UPDATE users SET avatar=? WHERE id=?", (avatar, uid))
    c.commit()
    fresh = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    c.close()
    return clean_row(fresh)


@router.post("/users/{uid}/profile")
def update_profile(uid: int, data: ProfileIn):
    """Profil maydonlarini tahrirlaydi (faqat berilganlari) va yangi holatini qaytaradi."""
    c = conn()
    u = c.execute("SELECT id FROM users WHERE id=?", (uid,)).fetchone()
    if u is None:
        c.close()
        raise HTTPException(404, "Foydalanuvchi topilmadi")
    for field in (
        "group", "age", "parents", "parent_phone",
        "phone", "address", "subject", "experience", "education", "about",
    ):
        val = getattr(data, field)
        if val is not None:
            c.execute(f'UPDATE users SET "{field}"=? WHERE id=?', (str(val).strip(), uid))
    c.commit()
    fresh = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    c.close()
    return clean_row(fresh)


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
