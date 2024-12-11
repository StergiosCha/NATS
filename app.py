from flask import Flask
from app.routes.text_routes import text_bp

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Register blueprints
    app.register_blueprint(text_bp, url_prefix='/api/text')
    
    return app

app = create_app()
