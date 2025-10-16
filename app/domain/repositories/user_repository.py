from domain.entities import UserEntity
from domain.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    model = UserEntity