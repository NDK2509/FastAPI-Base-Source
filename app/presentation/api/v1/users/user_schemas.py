from pydantic import BaseModel, Field, ConfigDict


class UserSchema(BaseModel):
    first_name: str
    last_name: str
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserSchema):
    password: str = Field(default="", min_length=8)
