"""Educative Viewer - Flask application factory and configuration."""

import os
from pathlib import Path

import jinja2
from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from os_utility import create_dir, delete_dir

db = SQLAlchemy()
ROOT_DIR = Path(__file__).parent.absolute()
# Use environment variable or fall back to home directory
_env_root = Path.home() / "EducativeViewer"
_custom_root = os.environ.get("EDUCATIVE_VIEWER_ROOT")
OS_ROOT = Path(_custom_root) if _custom_root else _env_root
DB_FILE_PATH = OS_ROOT / "db.sqlite"


def create_app() -> Flask:
    """Create and configure the Flask application."""
    create_dir(str(OS_ROOT))
    temp_folder_path = OS_ROOT / "temp"
    delete_dir(str(temp_folder_path))

    app = Flask(__name__, static_url_path="/edu-viewer/static")
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "dev-key-change-in-production",
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = str(temp_folder_path)

    # load course dir as templates folder
    course_dir = os.getenv("COURSE_DIR", ".")
    my_loader = jinja2.ChoiceLoader(
        [
            app.jinja_loader,
            jinja2.FileSystemLoader([str(ROOT_DIR / "templates"), f"{course_dir}"]),
        ],
    )
    app.jinja_loader = my_loader

    # set custom delimiters as html has many curly braces
    app.jinja_env.variable_start_string = "[([("
    app.jinja_env.variable_end_string = ")])]"
    app.jinja_env.block_start_string = "[([(="
    app.jinja_env.block_end_string = "=)])]"
    app.jinja_env.comment_start_string = "{[(#"
    app.jinja_env.comment_end_string = "#)]}"

    @app.before_request
    def create_tables() -> None:
        db.create_all()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', message="Page does not exist"), 404
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from models import User  # noqa: PLC0415

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        """Load user by ID for Flask-Login."""
        return db.session.get(User, int(user_id))

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint  # noqa: PLC0415

    app.register_blueprint(auth_blueprint, url_prefix="/edu-viewer")

    # blueprint for non-auth parts of app
    from main import main as main_blueprint  # noqa: PLC0415

    app.register_blueprint(main_blueprint, url_prefix="/edu-viewer")

    return app
