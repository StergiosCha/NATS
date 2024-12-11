from flask import Flask, render_template, request, jsonify
import os
import spacy

app = Flask(__name__, template_folder='app/templates')
nlp = spacy.load('el_core_news_md')

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    texts = {}
    
    for file in files:
        if file.filename:
            text = file.read().decode('utf-8')
            texts[file.filename] = text
            
    return render_template('results.html', files=texts)
