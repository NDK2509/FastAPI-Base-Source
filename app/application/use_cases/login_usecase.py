from sqlmodel import Session

from application.use_cases.base_usercase import BaseUseCase
from domain.entities import UserEntity
from domain.repositories.user_repository import UserRepository
from infrastructure.security.password_hasher import PasswordHasher
from presentation.api.v1.auth.auth_schemas import LoginSchema


class LoginUseCase(BaseUseCase):
    def __init__(self, session: Session):
        super().__init__(session)
        self.user_repository = UserRepository(session)
        self.password_hasher = PasswordHasher()

    def invoke(self, auth_data: LoginSchema) -> UserEntity | None:
        user = self.user_repository.get_by_username(auth_data.username)
        if user is None:
            return None
        if not self.password_hasher.verify(auth_data.password, user.password):
            return None
        return user
