from sqlmodel import Session

from application.use_cases.base_usercase import BaseUseCase
from domain.entities import UserEntity
from domain.repositories.user_repository import UserRepository
from fastapi_sso.sso.base import OpenID

class CreateOrGetGoogleUserUseCase(BaseUseCase):
    def __init__(self, session: Session):
        super().__init__(session)
        self.user_repository = UserRepository(session)

    def invoke(self, user_in: OpenID) -> UserEntity:
        user = self.user_repository.get_by_email(str(user_in.email))
        if user:
            return user

        username = str(user_in.email).split('@')[0]
        user = UserEntity(
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            email=str(user_in.email),
            username=username,
            avatar=user_in.picture
        )
        return self.user_repository.create(user)