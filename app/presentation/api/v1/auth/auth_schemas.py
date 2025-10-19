from pydantic import BaseModel

from presentation.api.v1.users.user_schemas import UserSchema


class LoginSchema(BaseModel):
    username: str
    password: str

class AuthSchema(BaseModel):
    user: UserSchema
    refresh_token: str
    access_token: str
