from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    first_name: str
    last_name: str
    username: str


class UserCreateSchema(UserSchema):
    password: str = Field(default="", min_length=8)
