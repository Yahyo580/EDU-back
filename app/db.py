"""Baza bilan ishlaydigan joy. Hech qanday sehr yo'q - oddiy sqlite3."""

import sqlite3
from pathlib import Path

from .config import DB_PATH


def _db_file():
    """DB_PATH papkasi yo'q bo'lsa uni yaratamiz. Iloji bo'lmasa (masalan Railway'da
    /data volume ulanmagan bo'lsa) xatoga yo'l qo'ymaymiz - lokal faylga tushamiz."""
    path = Path(DB_PATH)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)
    except OSError:
        return "edu.db"


_DB_FILE = _db_file()

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  name         TEXT UNIQUE NOT NULL,
  role         TEXT NOT NULL,              -- student | teacher | admin
  token        TEXT DEFAULT '',            -- ustoz/admin kirish tokeni
  password     TEXT DEFAULT '',            -- o'quvchi paroli
  status       TEXT DEFAULT 'viewer',      -- viewer = tomoshabin, student = o'quvchi
  "group"      TEXT DEFAULT '',
  age          TEXT DEFAULT '',
  parents      TEXT DEFAULT '',
  parent_phone TEXT DEFAULT '',
  phone        TEXT DEFAULT '',
  address      TEXT DEFAULT '',
  coins        INTEGER DEFAULT 0,
  added_by     TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS logins (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  name    TEXT,
  role    TEXT,
  status  TEXT,
  at      TEXT
);

CREATE TABLE IF NOT EXISTS attendance (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  date       TEXT NOT NULL,
  student_id INTEGER NOT NULL,
  status     TEXT NOT NULL,               -- keldi | kechikdi | yo'q
  coins      INTEGER DEFAULT 0,
  by_name    TEXT DEFAULT '',
  UNIQUE(date, student_id)
);

CREATE TABLE IF NOT EXISTS posts (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  author     TEXT,
  role       TEXT DEFAULT '',
  text       TEXT,
  media      TEXT DEFAULT '',             -- rasm/video (data URL yoki havola)
  media_type TEXT DEFAULT '',             -- image | video
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS comments (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER,
  author  TEXT,
  text    TEXT
);

CREATE TABLE IF NOT EXISTS schedule (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  day     TEXT NOT NULL,               -- Dushanba | Seshanba | ...
  time    TEXT NOT NULL,               -- 14:00 - 15:30
  subject TEXT NOT NULL,
  "group" TEXT DEFAULT '',
  teacher TEXT DEFAULT '',
  room    TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS homeworks (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  title      TEXT NOT NULL,
  "group"    TEXT DEFAULT '',
  subject    TEXT DEFAULT '',
  text       TEXT DEFAULT '',
  deadline   TEXT DEFAULT '',
  author     TEXT DEFAULT '',
  created_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS submissions (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  homework_id  INTEGER NOT NULL,
  student_id   INTEGER NOT NULL,
  student_name TEXT DEFAULT '',
  submitted_at TEXT DEFAULT '',
  UNIQUE(homework_id, student_id)
);

CREATE TABLE IF NOT EXISTS messages (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT DEFAULT '',
  contact    TEXT DEFAULT '',
  text       TEXT DEFAULT '',
  created_at TEXT DEFAULT ''
);
"""


def conn():
    """Har safar yangi ulanish ochamiz - kichik loyiha uchun shunisi yetarli."""
    c = sqlite3.connect(_DB_FILE)
    c.row_factory = sqlite3.Row
    return c


def init():
    """Jadvallarni yaratamiz. Eski bazada yangi ustunlar bo'lmasa - qo'shamiz."""
    c = conn()
    c.executescript(SCHEMA)

    have = {r["name"] for r in c.execute("PRAGMA table_info(users)")}
    for column in (
        "parent_phone", "address", "token", "avatar",
        "subject", "experience", "education", "about",
    ):
        if column not in have:
            c.execute(f"ALTER TABLE users ADD COLUMN {column} TEXT DEFAULT ''")

    have_posts = {r["name"] for r in c.execute("PRAGMA table_info(posts)")}
    for column in ("media_type", "role"):
        if column not in have_posts:
            c.execute(f"ALTER TABLE posts ADD COLUMN {column} TEXT DEFAULT ''")

    c.commit()
    c.close()


def clean_row(r):
    """Parolni tashqariga chiqarmaymiz."""
    if r is None:
        return None
    d = dict(r)
    d.pop("password", None)
    return d
