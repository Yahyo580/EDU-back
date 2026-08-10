"""Kichik yordamchi funksiyalar."""

import re
from datetime import datetime

from fastapi import HTTPException

from .config import NAME_PATTERN

NAME_RE = re.compile(NAME_PATTERN)
WORD_RE = re.compile(r"^[A-ZА-ЯЎҚҒҲ][a-zа-яўқғҳ']+$")


def clean_name(name: str) -> str:
    """Ortiqcha bo'shliqlarni olib tashlaymiz: '  ali   valiyev ' -> 'Ali Valiyev'."""
    return " ".join((name or "").split()).title()


def check_name(name: str) -> str:
    """Ism-familiya qoidalarga mosligini tekshiramiz:
    kamida 2 so'z, har bir so'z faqat harflardan va bitta katta harf bilan boshlanadi."""
    name = (name or "").strip()
    if not NAME_RE.match(name):
        raise HTTPException(400, "Ism familiya faqat harflardan iborat bo'lsin")

    parts = name.split()
    if len(parts) < 2:
        raise HTTPException(400, "Ism va familiyangizni kiriting (masalan: Mardiyev Yahyo)")

    for p in parts:
        if not WORD_RE.match(p):
            raise HTTPException(400, "Har bir so'z bitta katta harf bilan boshlansin (masalan: Mardiyev Yahyo)")

    return " ".join(parts).title()


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")
