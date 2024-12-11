# Open app/routes/text_routes.py and add this content:

from flask import Blueprint, request, jsonify, render_template
from app.models.doc_embeddings import DocEmbeddingsAnalyzer
from app.models.word_embeddings import WordEmbeddingsAnalyzer
from app.models.network_analyzer import NetworkAnalyzer
from app.models.ner_analyzer import NERAnalyzer
from app.models.dimension_reducer import DimensionReducer
import spacy
import os
from werkzeug.utils import secure_filename

text_bp = Blueprint('text', __name__)
nlp = spacy.load('el_core_news_md')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@text_bp.route('/upload', methods=['POST'])
def upload_files():
    """Handle multiple text file uploads"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    texts = {}
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            text = file.read().decode('utf-8')
            texts[filename] = nlp(text)
    
    if not texts:
        return jsonify({'error': 'No valid text files uploaded'}), 400
        
    return analyze_texts(texts)

@text_bp.route('/analyze', methods=['GET'])
def analyze_texts(texts):
    """Perform all analyses on the texts"""
    try:
        # Document embeddings
        doc_analyzer = DocEmbeddingsAnalyzer()
        doc_embeddings = doc_analyzer.create_embeddings(texts)
        doc_viz = doc_analyzer.visualize_embeddings('both')
        
        # Word embeddings
        word_analyzer = WordEmbeddingsAnalyzer()
        word_embeddings = word_analyzer.create_embeddings(texts)
        word_viz = word_analyzer.visualize_embeddings('both')
        
        # Network analysis
        network_analyzer = NetworkAnalyzer()
        network_results = {
            filename: network_analyzer.create_network(str(doc))
            for filename, doc in texts.items()
        }
        
        # NER analysis
        ner_analyzer = NERAnalyzer()
        ner_results = ner_analyzer.analyze_texts(texts)
        
        results = {
            'document_embeddings': doc_viz,
            'word_embeddings': word_viz,
            'network_analysis': network_results,
            'named_entities': ner_results
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@text_bp.route('/visualize/<analysis_type>', methods=['GET'])
def get_visualization(analysis_type):
    """Get specific visualization"""
    if analysis_type not in ['pca', 'tsne', 'network', 'ner']:
        return jsonify({'error': 'Invalid analysis type'}), 400
        
    return render_template(f'{analysis_type}_visualization.html')

@text_bp.route('/download/<result_type>', methods=['GET'])
def download_results(result_type):
    """Download analysis results"""
    if result_type not in ['embeddings', 'network', 'ner']:
        return jsonify({'error': 'Invalid result type'}), 400
        
    # Implementation for file downloads will go here
    pass
