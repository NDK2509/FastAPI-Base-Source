from fastapi.routing import APIRouter

from application.use_cases.create_user_usecase import CreateUserUseCase
from application.use_cases.get_all_users_usecase import GetAllUsersUseCase
from core.decorators import response_cache
from infrastructure.database.config import SessionDep
from presentation.api.v1.users.user_schemas import UserCreateSchema, UserSchema

user_router = APIRouter()


@user_router.get("/", response_model=list[UserSchema])
@response_cache(key_prefix="users")
async def get_all(session: SessionDep):
    return GetAllUsersUseCase(session).invoke()


@user_router.post("/", response_model=UserSchema)
async def create(data: UserCreateSchema, session: SessionDep):
    return CreateUserUseCase(session).invoke(data)
