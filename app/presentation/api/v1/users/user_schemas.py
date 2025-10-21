from datetime import date
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str | None = None
    birthday: date | None = None
    avatar: str | None = None


class UserCreateSchema(UserBase):
    password: str = Field(default="", min_length=8)


class UserSchema(UserBase):
    id: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        # 'v' is the raw value coming in (the UUID object)
        if isinstance(v, UUID):
            return str(v)
        return v
