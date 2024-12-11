from flask import Flask, render_template, request, jsonify
import os
import spacy
from app.models.doc_embeddings import DocEmbeddingsAnalyzer

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
    
    # Load and process texts
    for file in files:
        if file.filename:
            text = file.read().decode('utf-8')
            # Process with spaCy
            doc = nlp(text)
            texts[file.filename] = doc
            
    # Perform document embeddings analysis
    doc_analyzer = DocEmbeddingsAnalyzer()
    doc_embeddings = doc_analyzer.create_embeddings(texts)
    doc_viz = doc_analyzer.visualize_embeddings('both')
            
    return render_template('results.html', 
                         files=texts, 
                         doc_viz=doc_viz)
