from sqlmodel import or_

from application.use_cases.base_usercase import BaseUseCase
from core.app_exceptions import UserAlreadyExistsException, UsernameAlreadyExistsException, EmailAlreadyExistsException
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
        existing_user = self.user_repository.get_one_with_conditions([
           or_(UserEntity.username == user_in.username, UserEntity.email == user_in.email)
        ])

        if existing_user:
            if existing_user.username == user_in.username:
                raise UsernameAlreadyExistsException()
            if existing_user.email == user_in.email:
                raise EmailAlreadyExistsException()

        user_in.password = PasswordHasher.hash(user_in.password)
        user = UserEntity(**user_in.__dict__)
        return self.user_repository.create(user)
