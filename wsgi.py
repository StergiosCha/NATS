from flask import Flask, Blueprint, request, jsonify, render_template
from app.routes.text_routes import text_bp
import os

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(text_bp, url_prefix='/api/text')

@app.route('/')
def home():
    return "NATS is running!"
