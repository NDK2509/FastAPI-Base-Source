from application.use_cases.base_usercase import BaseUseCase
from domain.entities import UserEntity
from sqlmodel import Session

from domain.repositories.user_repository import UserRepository


class GetAllUsersUseCase(BaseUseCase):
    def __init__(self, session: Session):
        super().__init__(session)
        self.user_repository = UserRepository(session)

    def invoke(self) -> list[UserEntity]:
        return self.user_repository.get_all()