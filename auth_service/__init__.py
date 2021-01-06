import logging.config

from auth_service.database import db, migrate
from auth_service.extensions import cors, ma
from flask import Flask

from .config import config
from auth_service.oauth2 import config_oauth


def create_app(config_name="default", settings_override=None):
    init_logging()

    app = Flask(__name__)
    app_config = config[config_name]
    app.config.from_object(app_config)
    app_config.init_app(app)

    init_db(app)
    init_extensions(app)

    if settings_override:
        app.config.update(settings_override)

    init_blueprint(app)
    config_oauth(app)

    return app


def init_logging():
    LOGGING = {
        "version": 1,
        "formatters": {
            "brief": {"format": "%(message)s"},
            "default": {
                "format": "%(asctime)s %(levelname)-8s %(name)-15s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "none": {"class": "logging.NullHandler"},
        },
        "loggers": {
            "amqp": {"handlers": ["none"], "propagate": False},
            "conf": {"handlers": ["none"], "propagate": False},
            "": {
                "handlers": [
                    "console",
                ],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(LOGGING)


def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)


def init_extensions(app):
    cors.init_app(
        app,
        resources={
            r"/*": {"origins": "*"},
        },
    )
    ma.init_app(app)


def init_blueprint(app):
    from auth_service.api import api as api_bp
    from auth_service.oauth import oauth2 as oauth_bp
    from auth_service.swagger import swagger_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(oauth_bp, url_prefix="/oauth")
    app.register_blueprint(swagger_bp, url_prefix="/swagger")
