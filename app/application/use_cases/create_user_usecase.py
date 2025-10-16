from application.use_cases.base_usercase import BaseUseCase
from domain.entities import UserEntity
from domain.repositories.user_repository import UserRepository
from presentation.api.v1.users.user_schemas import UserCreateSchema
from infrastructure.security.password_hasher import PasswordHasher
from sqlmodel import Session


class CreateUserUseCase(BaseUseCase):
    def __init__(self, session: Session):
        super().__init__(session)
        self.user_repository = UserRepository(session)

    def invoke(self, user_in: UserCreateSchema) -> UserEntity:
        user_in.password = PasswordHasher.hash(user_in.password)
        user = UserEntity(**user_in.__dict__)
        return self.user_repository.create(user)
