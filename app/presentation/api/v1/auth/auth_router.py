from fastapi import HTTPException
from fastapi.routing import APIRouter

from application.use_cases.generate_auth_tokens_usecase import GenerateAuthTokensUseCase
from application.use_cases.login_usecase import LoginUseCase
from infrastructure.database.config import SessionDep
from presentation.api.v1.auth.auth_schemas import LoginSchema, AuthSchema
from presentation.api.v1.users.user_schemas import UserSchema

auth_router = APIRouter()


@auth_router.post(
    "/login",
    response_model=AuthSchema,
)
async def login(data: LoginSchema, session: SessionDep):
    user = LoginUseCase(session).invoke(data)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    user_info = UserSchema.model_validate(user)
    tokens = GenerateAuthTokensUseCase().invoke(user_info)
    return AuthSchema(
        user=user_info,
        refresh_token=tokens.refresh_token,
        access_token=tokens.access_token
    )


@auth_router.get("/logout")
async def logout():
    return {"message": "Logout here"}
