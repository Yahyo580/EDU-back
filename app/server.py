"""FastAPI ilovasi shu yerda yig'iladi."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import __version__
from .config import ALLOWED_ORIGINS
from .db import init
from .routes import attendance, auth, homework, leaderboard, messages, posts, schedule, users

app = FastAPI(title="EduCenter API", version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dastur ishga tushganda jadvallar tayyor turishi kerak.
init()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(attendance.router)
app.include_router(posts.router)
app.include_router(homework.router)
app.include_router(schedule.router)
app.include_router(leaderboard.router)
app.include_router(messages.router)


@app.get("/api/health")
def health():
    return {"ok": True, "version": __version__}


# Frontend build papkasi mavjud bo'lsa (Docker/ploy) uni xuddi shu origin orqali
# beramiz. Bunda /api so'rovlari birinchi navbatda API route'lariga boradi,
# qolgan barcha yo'llar esa React ilovasiga tushadi.
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
