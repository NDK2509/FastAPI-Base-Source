from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator

class UserSchema(BaseModel):
    id: str
    first_name: str
    last_name: str
    username: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        # 'v' is the raw value coming in (the UUID object)
        if isinstance(v, UUID):
            return str(v)
        # You could add other checks here if needed
        return v

class UserCreateSchema(UserSchema):
    password: str = Field(default="", min_length=8)
