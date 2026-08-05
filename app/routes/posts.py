"""E'lonlar: ustoz/admin yozadi, hamma ko'radi, hamma izoh qoldiradi."""

from fastapi import APIRouter, HTTPException

from ..config import MAX_MEDIA_CHARS
from ..db import clean_row, conn
from ..models import CommentIn, PostIn
from ..utils import now_text

router = APIRouter(prefix="/api/posts", tags=["posts"])


def all_posts(c):
    """E'lonlarni izohlari bilan birga qaytaramiz."""
    posts = [clean_row(r) for r in c.execute("SELECT * FROM posts ORDER BY id DESC")]
    for p in posts:
        rows = c.execute("SELECT * FROM comments WHERE post_id=? ORDER BY id", (p["id"],))
        p["comments"] = [dict(r) for r in rows]
    return posts


@router.get("")
def get_posts():
    c = conn()
    out = all_posts(c)
    c.close()
    return out


@router.post("")
def create_post(data: PostIn):
    text = (data.text or "").strip()
    media = data.media or ""

    if not text and not media:
        raise HTTPException(400, "E'lon bo'sh bo'lmasin - matn yoki rasm qo'shing")
    if len(media) > MAX_MEDIA_CHARS:
        raise HTTPException(400, "Fayl juda katta. 4MB gacha rasm tanlang")

    media_type = data.media_type or ("video" if media.startswith("data:video") else "image")

    c = conn()
    c.execute(
        "INSERT INTO posts(author, role, text, media, media_type, created_at)"
        " VALUES(?,?,?,?,?,?)",
        (data.author, data.role, text, media, media_type if media else "", now_text()),
    )
    c.commit()
    out = all_posts(c)
    c.close()
    return out


@router.delete("/{pid}")
def delete_post(pid: int):
    c = conn()
    c.execute("DELETE FROM posts WHERE id=?", (pid,))
    c.execute("DELETE FROM comments WHERE post_id=?", (pid,))
    c.commit()
    out = all_posts(c)
    c.close()
    return out


@router.post("/{pid}/comments")
def add_comment(pid: int, data: CommentIn):
    text = (data.text or "").strip()
    if not text:
        raise HTTPException(400, "Izoh bo'sh")
    c = conn()
    c.execute(
        "INSERT INTO comments(post_id, author, text) VALUES(?,?,?)",
        (pid, data.author, text),
    )
    c.commit()
    out = all_posts(c)
    c.close()
    return out
