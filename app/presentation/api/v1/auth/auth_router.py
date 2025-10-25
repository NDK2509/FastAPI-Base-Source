from fastapi import Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.routing import APIRouter
from fastapi_sso import GoogleSSO

from application.use_cases.create_or_get_google_user_usecase import CreateOrGetGoogleUserUseCase
from application.use_cases.generate_auth_tokens_usecase import GenerateAuthTokensUseCase
from application.use_cases.login_usecase import LoginUseCase
from core.app_exceptions import InvalidCredentialsException
from core.dependencies import get_settings
from infrastructure.database.config import SessionDep
from presentation.api.v1.auth.auth_schemas import LoginSchema, AuthSchema
from presentation.api.v1.users.user_schemas import UserSchema

settings = get_settings()
auth_router = APIRouter()


@auth_router.post(
    "/login",
    response_model=AuthSchema,
)
async def login(data: LoginSchema, session: SessionDep, response: Response):
    user = LoginUseCase(session).invoke(data)
    if not user:
        raise InvalidCredentialsException()

    user_info = UserSchema.model_validate(user)
    tokens = GenerateAuthTokensUseCase().invoke(user_info)
    auth_data = AuthSchema(
        user=user_info,
        refresh_token=tokens.refresh_token,
        access_token=tokens.access_token
    )
    response.set_cookie("refresh_token", tokens.refresh_token)
    response.set_cookie("access_token", tokens.access_token)
    return auth_data


@auth_router.get("/logout")
async def logout():
    response = JSONResponse(
        content={"msg": "Logout successful!"},
        status_code=200,
    )
    response.delete_cookie("refresh_token")
    response.delete_cookie("access_token")
    return response

if settings.google_client_id:
    google_sso = GoogleSSO(
        settings.google_client_id,
        settings.google_client_secret,
        settings.google_redirect_url,
        allow_insecure_http=settings.env == "development"
    )

    @auth_router.get("/google/login")
    async def google_login():
        """
        Redirects the user to Google's login page.
        """
        # 'async with' is required for the library to manage its internal state
        async with google_sso:
            return await google_sso.get_login_redirect()


    @auth_router.get("/google/callback", response_model=AuthSchema)
    async def google_callback(request: Request, session: SessionDep):
        """
        This is the endpoint Google redirects to after login.
        It processes the user's information and returns it.
        """
        async with google_sso:
            # Verify and process the request to get the user's details
            gg_user = await google_sso.verify_and_process(request)

        response = RedirectResponse(url="/")
        if gg_user:
            user = CreateOrGetGoogleUserUseCase(session).invoke(gg_user)
            user_info = UserSchema.model_validate(user)
            tokens = GenerateAuthTokensUseCase().invoke(user_info)
            response.set_cookie("refresh_token", tokens.refresh_token)
            response.set_cookie("access_token", tokens.access_token)

        return response
