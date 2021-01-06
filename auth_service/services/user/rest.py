import requests

from auth_service.domain.user import UserEntity
from auth_service.services.user.base import BaseUserService


class UserService(BaseUserService):
    def __init__(self, endpoint=None):
        self.endpoint = endpoint.rstrip("/")

    def get(self, user_id):
        endpoint = f"{self.endpoint}/api/users/{user_id}"
        resp = requests.get(endpoint)

        if resp.status_code == 200:
            user_dict = resp.json()
            return UserEntity.from_dict(
                {"username": user_dict["email"], "id": user_dict["id"]}
            )

        return None

    def get_by_username(self, username):
        endpoint = f"{self.endpoint}/api/users/get_by_email/{username}"
        resp = requests.get(endpoint)

        if resp.status_code == 200:
            return resp.json()

        return None

    def authenticate(self, username, password):
        endpoint = f"{self.endpoint}/api/authenticate"
        resp = requests.post(
            endpoint, json={"username": username, "password": password}
        )

        try:
            return resp.json().get("is_authenticated")
        except Exception as e:
            return False

    def authenticate_and_get_user(self, username, password):
        endpoint = f"{self.endpoint}/api/authenticate"
        resp = requests.post(
            endpoint, json={"username": username, "password": password}
        )
        if resp.status_code != 200:
            return None

        user_dict = resp.json().get("user")
        if user_dict is None:
            return None

        return UserEntity.from_dict(
            {"username": user_dict["email"], "id": user_dict["id"]}
        )
