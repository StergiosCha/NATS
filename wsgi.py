from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder='app/templates')

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected'}), 400
        
    return jsonify({'message': 'Files received successfully'})
