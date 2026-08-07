"""API yo'llari shu papkada, har bir mavzu alohida faylda."""

from . import attendance, auth, homework, leaderboard, messages, posts, schedule, users

__all__ = ["auth", "users", "attendance", "posts", "homework", "schedule", "leaderboard", "messages"]
