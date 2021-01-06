from auth_service.domain.user import UserEntity
from auth_service.services.user.base import BaseUserService

MOCK_USERS = [
    UserEntity(id=1, username="john", ),
    UserEntity(id=2, username="jane", ),
]


class MockUserService(BaseUserService):
    def __init__(self):
        pass

    def get(self, user_id):
        for user in MOCK_USERS:
            if str(user.id) == str(user_id):
                return user

        return None

    def get_by_username(self, username):
        for user in MOCK_USERS:
            if user.username == username:
                return user

        return None

    def authenticate(self, username, password):
        for user in MOCK_USERS:
            if user.username == username:
                return True

        return False

    def authenticate_and_get_user(self, username, password):
        return self.get_by_username(username)
