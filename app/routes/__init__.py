from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Import and register blueprints
    from app.routes.auth import auth as auth_blueprint
    from app.routes.main import main as main_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    return app
