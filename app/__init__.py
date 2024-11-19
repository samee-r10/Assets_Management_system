import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Set up logging
    if not os.path.exists('app/logs'):
        os.makedirs('app/logs')
    handler = RotatingFileHandler('app/logs/inventory_app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # Import blueprints and register them
    from app.routes.auth import auth as auth_blueprint
    from app.routes.main import main as main_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    print(app.url_map)

    with app.app_context():
        # Import models here to avoid circular import issues
        from app.models import User

        # Create database tables
        db.create_all()

        # Create users if they don't exist

        if not User.query.filter_by(username='Admin').first():
            Admin = User(username='Admin')
            Admin.set_password(os.getenv('ADMIN_PASSWORD', 'Admin@123'))
            db.session.add(Admin)

        db.session.commit()

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
