from flask import Flask, Blueprint, request, jsonify, render_template
from app.routes.text_routes import text_bp
import os

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(text_bp, url_prefix='/api/text')

@app.route('/')
def home():
    return render_template('upload.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
