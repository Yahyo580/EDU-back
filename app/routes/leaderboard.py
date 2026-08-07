"""Reyting: o'quvchilar coin va davomat bo'yicha tartiblanadi."""

from fastapi import APIRouter

from ..db import conn

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("")
def leaderboard(limit: int = 50):
    """O'quvchilarni coin bo'yicha tartiblab, davomat sonini ham qaytaradi."""
    c = conn()
    rows = c.execute(
        "SELECT id, name, \"group\", coins FROM users"
        " WHERE role='student' ORDER BY coins DESC, name"
    ).fetchall()

    out = []
    rank = 0
    last_coins = None
    for r in rows:
        d = dict(r)
        attended = c.execute(
            "SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='keldi'",
            (d["id"],),
        ).fetchone()[0]
        late = c.execute(
            "SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='kechikdi'",
            (d["id"],),
        ).fetchone()[0]
        # Bir xil coin egalariga bir xil o'rin beramiz.
        if d["coins"] != last_coins:
            rank += 1
            last_coins = d["coins"]
        out.append({
            "id": d["id"],
            "name": d["name"],
            "group": d["group"],
            "coins": d["coins"],
            "attended": attended,
            "late": late,
            "rank": rank,
        })
        if len(out) >= limit:
            break
    c.close()
    return out
