"""Baza bilan ishlaydigan joy. Hech qanday sehr yo'q - oddiy sqlite3."""

import sqlite3

from .config import DB_PATH

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
"""


def conn():
    """Har safar yangi ulanish ochamiz - kichik loyiha uchun shunisi yetarli."""
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init():
    """Jadvallarni yaratamiz. Eski bazada yangi ustunlar bo'lmasa - qo'shamiz."""
    c = conn()
    c.executescript(SCHEMA)

    have = {r["name"] for r in c.execute("PRAGMA table_info(users)")}
    for column in ("parent_phone", "address", "token"):
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
