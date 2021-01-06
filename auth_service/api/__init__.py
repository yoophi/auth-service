from authlib.integrations.flask_oauth2 import current_token
from flask import Blueprint
from flask import jsonify

from auth_service.oauth2 import require_oauth

api = Blueprint("api", __name__)


@api.route("/me")
@require_oauth("profile")
def api_me():
    user_id = current_token.user_id
    return jsonify(user_id=user_id)
