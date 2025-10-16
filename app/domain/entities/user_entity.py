import uuid

from sqlmodel import SQLModel, Field

from domain.entities.base import SoftDeleteMixin, TimeMixin


class UserEntity(SQLModel, TimeMixin, SoftDeleteMixin, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    first_name: str
    last_name: str
    username: str = Field(unique=True)
    password: str
