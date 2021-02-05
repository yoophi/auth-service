import time
import os

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
from authlib.oauth2.rfc7009 import RevocationEndpoint as _RevocationEndpoint
from authlib.oauth2.rfc7662 import IntrospectionEndpoint as _IntrospectionEndpoint
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
from auth_service.models import OAuth2Client, OAuth2AuthorizationCode, OAuth2Token, User
from auth_service.user import user_manager

JWT_CONFIG = {
    "key": os.environ.get("OAUTH2_JWT_SECRET_KEY", "secret-key"),
    "alg": "HS256",
    "iss": os.environ.get("OAUTH2_JWT_ISS", "https://authlib.org"),
    "exp": 3600,
}


def exists_nonce(nonce, req):
    exists = (
        db.session.query(OAuth2AuthorizationCode)
        .filter_by(client_id=req.client_id, nonce=nonce)
        .first()
    )
    return bool(exists)


def generate_user_info(user, scope):
    return UserInfo(sub=str(user.id), name=user.email)


def create_authorization_code(client, grant_user, request):
    code = gen_salt(48)
    nonce = request.data.get("nonce")
    client_id = client.client_id
    redirect_uri = request.redirect_uri
    scope = request.scope
    user_id = grant_user.id

    item = OAuth2AuthorizationCode(
        code=code,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        user_id=user_id,
        nonce=nonce,
    )
    db.session.add(item)
    db.session.commit()
    return code


class AuthorizationCodeGrant(_AuthorizationCodeGrant):
    def create_authorization_code(self, client, grant_user, request):
        return create_authorization_code(client, grant_user, request)

    def parse_authorization_code(self, code, client):
        item = (
            db.session.query(OAuth2AuthorizationCode)
            .filter_by(code=code, client_id=client.client_id)
            .first()
        )
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        try:
            db.session.delete(authorization_code)
            db.session.commit()
        except Exception as e:
            current_app.logger.exception(type(e))

    def authenticate_user(self, authorization_code):
        return db.session.query(User).get(authorization_code.user_id)


class ResourceOwnerPasswordCredentialsGrant(_ResourceOwnerPasswordCredentialsGrant):
    def authenticate_user(self, username, password):
        user = (
            db.session.query(User)
            .filter(
                User.email == username,
            )
            .first()
        )
        if user is not None and user_manager.verify_password(password, user.password):
            return user

        return None


class RefreshTokenGrant(_RefreshTokenGrant):
    INCLUDE_NEW_REFRESH_TOKEN = True

    def revoke_old_credential(self, credential):
        db.session.delete(credential)
        db.session.commit()

    def authenticate_refresh_token(self, refresh_token):
        token = (
            db.session.query(OAuth2Token)
            .filter_by(
                refresh_token=refresh_token,
                revoked=False,
            )
            .first()
        )
        if token and not token.is_refresh_token_expired():
            return token

    def authenticate_user(self, credential):
        return db.session.query(User).get(credential.user_id)


class OpenIDCode(_OpenIDCode):
    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_jwt_config(self, grant):
        return JWT_CONFIG

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


class ImplicitGrant(_OpenIDImplicitGrant):
    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_jwt_config(self, grant):
        return JWT_CONFIG

    def generate_user_info(self, user, scope):
        return generate_user_info(user, scope)


class HybridGrant(_OpenIDHybridGrant):
    def create_authorization_code(self, client, grant_user, request):
        return create_authorization_code(client, grant_user, request)

    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_jwt_config(self):
        return JWT_CONFIG

    def generate_user_info(self, user, scope):
        return generate_user_info(user, scope)


class RevocationEndpoint(_RevocationEndpoint):
    def query_token(self, token, token_type_hint, client):
        q = db.session.query(OAuth2Token).filter_by(client_id=client.client_id)

        if token_type_hint == "access_token":
            return q.filter_by(access_token=token).first()
        elif token_type_hint == "refresh_token":
            return q.filter_by(refresh_token=token).first()
        # without token_type_hint
        item = q.filter_by(access_token=token).first()
        if item:
            return item
        return q.filter_by(refresh_token=token).first()

    def revoke_token(self, token):
        token.revoked = True
        db.session.add(token)
        db.session.commit()


class IntrospectionEndpoint(_IntrospectionEndpoint):
    def introspect_token(self, token: OAuth2Token):
        active = self.is_token_active(token)
        user = db.session.query(User).get(token.user_id)
        return {
            "active": active,
            "client_id": token.client_id,
            "token_type": token.token_type,
            "username": user.email,
            "scope": token.get_scope(),
            "sub": user.id,
            "aud": token.client_id,
            "iss": "https://server.example.com/",
            "exp": (token.issued_at + token.expires_in),
            "iat": token.issued_at,
        }

    def query_token(self, token, token_type_hint, client):
        if token_type_hint == "access_token":
            token = db.session.query(OAuth2Token).filter_by(access_token=token).first()
        elif token_type_hint == "refresh_token":
            token = db.session.query(OAuth2Token).filter_by(refresh_token=token).first()
        else:
            # without token_type_hint
            token = db.session.query(OAuth2Token).filter_by(access_token=token).first()
            if not token:
                token = (
                    db.session.query(OAuth2Token).filter_by(refresh_token=token).first()
                )
        if token:
            if token.client_id == client.client_id:
                return token

    def is_token_active(self, token: OAuth2Token) -> bool:
        return not token.revoked and token.get_expires_at() > time.time()


authorization = AuthorizationServer()
require_oauth = ResourceProtector()


def config_oauth(app):
    query_client = create_query_client_func(db.session, OAuth2Client)
    save_token = create_save_token_func(db.session, OAuth2Token)
    authorization.init_app(app, query_client=query_client, save_token=save_token)

    # support all openid grants
    authorization.register_grant(
        AuthorizationCodeGrant,
        [
            OpenIDCode(require_nonce=True),
        ],
    )

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

    authorization.register_grant(ImplicitGrant)

    authorization.register_grant(HybridGrant)

    authorization.register_endpoint(RevocationEndpoint)

    authorization.register_endpoint(IntrospectionEndpoint)

    # protect resource
    bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())
