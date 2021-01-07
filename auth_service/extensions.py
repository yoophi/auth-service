from flask_cors import CORS
from flask_login import LoginManager
from flask_marshmallow import Marshmallow

cors = CORS()
ma = Marshmallow()
login_manager = LoginManager()
