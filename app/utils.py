"""Kichik yordamchi funksiyalar."""

import re
from datetime import datetime

from fastapi import HTTPException

from .config import NAME_PATTERN

NAME_RE = re.compile(NAME_PATTERN)


def clean_name(name: str) -> str:
    """Ortiqcha bo'shliqlarni olib tashlaymiz: '  ali   valiyev ' -> 'Ali Valiyev'."""
    return " ".join((name or "").split()).title()


def check_name(name: str) -> str:
    """Ism to'g'ri yozilganini tekshiramiz, bo'lmasa xato qaytaramiz."""
    name = clean_name(name)
    if not NAME_RE.match(name):
        raise HTTPException(400, "Ism familiya faqat harflardan iborat bo'lsin")
    return name


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")
