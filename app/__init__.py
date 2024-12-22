# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

    # Register blueprint
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
