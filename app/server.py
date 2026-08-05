"""FastAPI ilovasi shu yerda yig'iladi."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import ALLOWED_ORIGINS
from .db import init
from .routes import attendance, auth, posts, users

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


@app.get("/api/health")
def health():
    return {"ok": True, "version": __version__}
