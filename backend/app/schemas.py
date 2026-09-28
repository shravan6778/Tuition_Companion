import re
import uuid

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import ChapterStatus, Role, RoomType


PHONE_RE = re.compile(r"^\+?[0-9]{10,15}$")


def normalize_phone(value: str) -> str:
    value = re.sub(r"[\s\-()]", "", value)

    if not PHONE_RE.match(value):
        raise ValueError("Enter a valid phone number")

    return value

#username added
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    username: str
    phone: str
    role: Role
    link_code: str | None = None


class RoomCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    room_type: RoomType


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    room_type: RoomType
    join_code: str
    created_at: datetime
    member_count: int = 0


class MemberOut(BaseModel):
    id: uuid.UUID
    name: str
    joined_at: datetime


class JoinRoomIn(BaseModel):
    join_code: str = Field(min_length=4, max_length=12)

    @field_validator("join_code")
    @classmethod
    def upper(cls, v: str) -> str:
        return v.strip().upper()


class LinkStudentIn(BaseModel):
    link_code: str = Field(min_length=4, max_length=12)

    @field_validator("link_code")
    @classmethod
    def upper(cls, v: str) -> str:
        return v.strip().upper()


class RoomBrief(BaseModel):
    id: uuid.UUID
    name: str


class ChildOut(BaseModel):
    id: uuid.UUID
    name: str
    rooms: list[RoomBrief]
    
    
class SubjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    grade: str | None = Field(default=None, max_length=20)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    grade: str | None = None
    created_at: datetime
    chapter_count: int = 0


class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID
    title: str
    position: int
    status: ChapterStatus
    error_message: str | None = None
    created_at: datetime