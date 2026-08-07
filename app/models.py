"""Frontend yuboradigan ma'lumot shakllari."""

from typing import Optional

from pydantic import BaseModel


class LoginIn(BaseModel):
    role: str                 # student | teacher | admin
    name: str
    secret: str               # o'quvchi uchun parol, ustoz/admin uchun token


class StatusIn(BaseModel):
    status: str


class StudentIn(BaseModel):
    """Ustoz yoki admin o'quvchi qo'shganda to'ldiriladigan forma."""
    name: str
    group: str = ""
    age: str = ""
    parents: str = ""          # ota-ona ismi
    parent_phone: str = ""     # ota-ona telefoni
    phone: str = ""            # o'quvchining o'z raqami
    address: str = ""          # yashash joyi
    added_by: str = ""


class CoinsIn(BaseModel):
    delta: int


class MarkIn(BaseModel):
    date: str
    student_id: int
    status: str
    coins: int = 0
    by: str = ""


class PostIn(BaseModel):
    author: str
    role: str = ""
    text: str = ""
    media: Optional[str] = ""       # data URL (rasm/video) yoki oddiy havola
    media_type: Optional[str] = ""  # image | video


class CommentIn(BaseModel):
    author: str
    text: str


class ScheduleIn(BaseModel):
    day: str
    time: str = ""
    subject: str
    group: str = ""
    teacher: str = ""
    room: str = ""


class HomeworkIn(BaseModel):
    title: str
    group: str = ""
    subject: str = ""
    text: str = ""
    deadline: str = ""
    author: str = ""


class SubmitIn(BaseModel):
    student_id: int
    student_name: str = ""
    done: bool = True


class AvatarIn(BaseModel):
    avatar: str = ""


class MessageIn(BaseModel):
    name: str = ""
    contact: str = ""
    text: str


class ProfileIn(BaseModel):
    """Profilni tahrirlash: faqat berilgan (None emas) maydonlar yangilanadi."""
    group: Optional[str] = None
    age: Optional[str] = None
    parents: Optional[str] = None
    parent_phone: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    subject: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    about: Optional[str] = None
