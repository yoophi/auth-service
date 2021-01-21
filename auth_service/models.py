import time

from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2TokenMixin,
    OAuth2AuthorizationCodeMixin,
)
from flask_user import UserMixin

from auth_service.database import db


class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = "oauth2_client"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
    )


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = "oauth2_code"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
    )


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = "oauth2_token"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
    )

    def get_nonce(self):
        return None

    def get_auth_time(self):
        return None

    def is_refresh_token_expired(self):
        return time.time() > (self.issued_at + self.expires_in + 60 * 24 * 30)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column("is_active", db.Boolean(), nullable=False, server_default="1")

    # User authentication information. The  is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(
        db.String(
            255,
        ),
        nullable=False,
        unique=True,
    )
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default="")

    # User information
    first_name = db.Column(
        db.String(
            100,
        ),
        nullable=False,
        server_default="",
    )
    last_name = db.Column(
        db.String(
            100,
        ),
        nullable=False,
        server_default="",
    )

    # Define the relationship to Role via UserRoles
    roles = db.relationship("Role", secondary="user_roles")


# Define the Role data-model
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    role_id = db.Column(db.Integer(), db.ForeignKey("roles.id", ondelete="CASCADE"))
