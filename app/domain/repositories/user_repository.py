from domain.entities import UserEntity
from domain.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    model = UserEntity

    def get_by_username(self, username: str) -> UserEntity | None:
        return self.get_one_with_filters({
            UserEntity.username.name: username
        })