import uuid

from sqlmodel import SQLModel, Field
from datetime import date

from domain.entities.base import SoftDeleteMixin, TimeMixin


class UserEntity(SQLModel, TimeMixin, SoftDeleteMixin, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    first_name: str
    last_name: str
    username: str = Field(unique=True)
    password: str | None = Field(default=None, nullable=True)
    email: str | None = Field(default=None, unique=True, nullable=True)
    birthday: date | None = Field(default=None, nullable=True)
    avatar: str | None = Field(default=None, nullable=True)
