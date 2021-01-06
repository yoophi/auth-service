from flask import (
    Blueprint,
)

from auth_service.oauth2 import authorization

oauth2 = Blueprint("oauth2", __name__)


@oauth2.route("/token", methods=["POST"])
def issue_token():
    return authorization.create_token_response()
