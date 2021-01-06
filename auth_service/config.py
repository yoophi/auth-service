import os

APP_DIR = os.path.dirname(__file__)

DEFAULT_SECRET_KEY = "Uphooh4CheiQuoosez8Shieb9aesu1taeHa6cheiThuud2taijoh0kei2ush2sie"

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "oidc")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "secret11!")
DB_DATABASE = os.environ.get("DB_DATABASE", "oidc")
DB_ENGINE = os.environ.get("DB_ENGINE", "postgres")
DB_SCHEME = "postgres+psycopg2"

if DB_ENGINE == "mysql":
    DB_SCHEME = "mysql+mysqlconnector"

SQLALCHEMY_DATABASE_URI = (
    f"{DB_SCHEME}://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/"
    f"{DB_DATABASE}"
)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or DEFAULT_SECRET_KEY

    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OAUTH2_REFRESH_TOKEN_GENERATOR = True
    MOCK_USER_SERVICE = bool(os.environ.get('MOCK_USER_SERVICE'))

    USER_API_URL = ""

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class DockerConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler

        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.INFO)
        app.logger.addHandler(syslog_handler)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "docker": DockerConfig,
    "unix": UnixConfig,
    "default": DevelopmentConfig,
}
