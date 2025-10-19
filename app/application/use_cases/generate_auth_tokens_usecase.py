from infrastructure.security.jwt_handler import JwtHandler
from presentation.api.v1.users.user_schemas import UserSchema
from pydantic import BaseModel


class TokensOutput(BaseModel):
    access_token: str
    refresh_token: str


class GenerateAuthTokensUseCase:
    def invoke(self, user: UserSchema) -> TokensOutput:
        payload = user.model_dump()
        access_token = JwtHandler.generate_access_token(payload)
        refresh_token = JwtHandler.generate_refresh_token(payload)
        return TokensOutput(access_token=access_token, refresh_token=refresh_token)
