import os

from auth_service import create_app

app = create_app(os.environ.get("FLASK_CONFIG", "default"))
