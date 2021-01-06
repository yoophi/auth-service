from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector
from authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_save_token_func,
    create_bearer_token_validator,
)
from authlib.oauth2.rfc6749.grants import (
    AuthorizationCodeGrant as _AuthorizationCodeGrant,
    ResourceOwnerPasswordCredentialsGrant as _ResourceOwnerPasswordCredentialsGrant,
    RefreshTokenGrant as _RefreshTokenGrant,
)
from authlib.oidc.core import UserInfo
from authlib.oidc.core.grants import (
    OpenIDCode as _OpenIDCode,
    OpenIDImplicitGrant as _OpenIDImplicitGrant,
    OpenIDHybridGrant as _OpenIDHybridGrant,
)
from authlib.oidc.core.grants.util import generate_id_token, is_openid_scope
from flask import current_app
from werkzeug.security import gen_salt

from auth_service.database import db
from auth_service.models import OAuth2Client, OAuth2AuthorizationCode, OAuth2Token
from auth_service.services import user_service

DUMMY_JWT_CONFIG = {
    "key": "secret-key",
    "alg": "HS256",
    "iss": "https://authlib.org",
    "exp": 3600,
}


def exists_nonce(nonce, req):
    exists = db.session.query(OAuth2AuthorizationCode).filter_by(
        client_id=req.client_id, nonce=nonce
    ).first()
    return bool(exists)


def generate_user_info(user, scope):
    return UserInfo(sub=str(user.id), name=user.username)


class ResourceOwnerPasswordCredentialsGrant(_ResourceOwnerPasswordCredentialsGrant):
    def authenticate_user(self, username, password):
        return user_service.authenticate_and_get_user(username, password)


class RefreshTokenGrant(_RefreshTokenGrant):
    INCLUDE_NEW_REFRESH_TOKEN = True

    def revoke_old_credential(self, credential):
        db.session.delete(credential)
        db.session.commit()

    def authenticate_refresh_token(self, refresh_token):
        token = db.session.query(OAuth2Token).filter_by(refresh_token=refresh_token).first()
        # if token and not token.is_refresh_token_expired():
        if token:
            return token

    def authenticate_user(self, credential):
        return user_service.get(credential.user_id)


class OpenIDCode(_OpenIDCode):
    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_jwt_config(self, grant):
        return DUMMY_JWT_CONFIG

    def generate_user_info(self, user, scope):
        return generate_user_info(user, scope)

    def process_token(self, grant, token):
        scope = token.get("scope")
        if not scope or not is_openid_scope(scope):
            # standard authorization code flow
            return token

        request = grant.request
        credential = request.credential

        jwt_config = self.get_jwt_config(grant)
        jwt_config["aud"] = self.get_audiences(request)
        if credential is not None:
            jwt_config["nonce"] = credential.get_nonce()
            jwt_config["auth_time"] = credential.get_auth_time()

        user_info = self.generate_user_info(request.user, token["scope"])
        id_token = generate_id_token(token, user_info, **jwt_config)
        token["id_token"] = id_token

        return token


authorization = AuthorizationServer()
require_oauth = ResourceProtector()


def config_oauth(app):
    query_client = create_query_client_func(db.session, OAuth2Client)
    save_token = create_save_token_func(db.session, OAuth2Token)
    authorization.init_app(app, query_client=query_client, save_token=save_token)

    authorization.register_grant(
        ResourceOwnerPasswordCredentialsGrant,
        [
            OpenIDCode(require_nonce=False),
        ],
    )

    authorization.register_grant(
        RefreshTokenGrant,
        [
            OpenIDCode(require_nonce=True),
        ],
    )

    # protect resource
    bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())
