from flask import g, current_app
from werkzeug.local import LocalProxy

from auth_service.services.user.base import BaseUserService
from auth_service.services.user.mock import MockUserService
from auth_service.services.user.rest import UserService


def get_repo():
    if "user_service" not in g:
        if current_app.config.get('MOCK_USER_SERVICE'):
            service = MockUserService()
        else:
            endpoint = current_app.config.get('USER_API_URL')
            service = UserService(endpoint=endpoint)

        g.user_service = service

    return g.user_service


# noinspection PyTypeChecker
user_service: BaseUserService = LocalProxy(get_repo)
