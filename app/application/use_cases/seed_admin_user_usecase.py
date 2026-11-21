from sqlmodel import Session

from application.use_cases.base_usercase import BaseUseCase
from domain.entities import UserEntity
from domain.repositories.user_repository import UserRepository
from infrastructure.security.password_hasher import PasswordHasher


class SeedAdminUserUseCase(BaseUseCase):
    """Ensure the initial system administrator account exists."""

    def __init__(self, session: Session):
        super().__init__(session)
        self.user_repository = UserRepository(session)

    def invoke(self, username: str, password: str) -> UserEntity | None:
        normalized_username = username.strip()
        if not normalized_username or not password:
            return None

        existing_user = self.user_repository.get_by_username(normalized_username)
        if existing_user is not None:
            return existing_user

        admin_user = UserEntity(
            first_name="System",
            last_name="Admin",
            username=normalized_username,
            password=PasswordHasher.hash(password),
        )
        return self.user_repository.create(admin_user)
