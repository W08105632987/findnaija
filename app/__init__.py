from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import os

# Extensions (Global)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)  # Looks for 'instance/' folder

    # Set secret key
    app.config['SECRET_KEY'] = 'yoursecretkey'

    # Full path to site.db inside instance folder
    db_path = os.path.join(app.instance_path, 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    # Print DB path for confirmation (optional)
    print("[✔] Database path:", db_path)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprint(s)
    from app.routes import main
    app.register_blueprint(main)

    return app
