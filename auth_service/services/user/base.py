import abc
from typing import Optional

from auth_service.domain.user import UserEntity


class BaseUserService(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, user_id) -> Optional[UserEntity]:
        pass

    @abc.abstractmethod
    def get_by_username(self, username) -> Optional[UserEntity]:
        pass

    @abc.abstractmethod
    def authenticate(self, username, password) -> bool:
        pass

    @abc.abstractmethod
    def authenticate_and_get_user(self, username, password) -> Optional[UserEntity]:
        pass
