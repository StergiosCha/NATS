# app/routes/text_routes.py

from flask import Blueprint, request, jsonify, render_template, current_app
from app.models.doc_embeddings import EnhancedDocEmbeddingAnalyzer
from app.models.network_analyzer import EnhancedNetworkAnalyzer
from app.models.ner_analyzer import EnhancedNERAnalyzer
import os
from werkzeug.utils import secure_filename
import json

text_bp = Blueprint('text', __name__)

UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'app/static'
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@text_bp.route('/')
def index():
    """Main upload page"""
    print("=" * 50)
    print("LOADING INDEX PAGE")
    print(f"Template path: {current_app.template_folder}")
    print("=" * 50)
    return render_template('index.html')
@text_bp.route('/api/analyze', methods=['POST'])
def analyze():
    """Handle file upload and analysis"""
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        analysis_type = request.form.get('analysis_type', 'doc2vec')
        
        # Read texts from files
        texts = {}
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                text = file.read().decode('utf-8')
                texts[filename] = text
        
        if not texts:
            return jsonify({'error': 'No valid text files uploaded'}), 400
        
        print(f"Processing {len(texts)} files with analysis type: {analysis_type}")
        
        # Perform analysis based on type
        if analysis_type == 'doc2vec':
            analyzer = EnhancedDocEmbeddingAnalyzer()
            embedding_type = request.form.get('embedding_type', 'sentence_transformer')
            reduction_method = request.form.get('reduction_method', 'pca')
            
            result = analyzer.create_comprehensive_visualization(
                texts, 
                embedding_type=embedding_type,
                reduction_method=reduction_method
            )
            
            # Parse JSON strings to dicts for template rendering
            parsed_result = {
                'scatter_plot': json.loads(result['scatter_plot']) if isinstance(result['scatter_plot'], str) else result['scatter_plot'],
                'features_chart': json.loads(result['features_chart']) if isinstance(result['features_chart'], str) else result['features_chart'],
                'similarity_heatmap': json.loads(result['similarity_heatmap']) if isinstance(result['similarity_heatmap'], str) else result['similarity_heatmap'],
                'filenames': result['filenames'],
                'embeddings': result['embeddings'],
                'features': result['features'],
                'clusters': result['clusters']
            }
            
            return render_template('results.html',
                                 analysis_type='doc2vec',
                                 files={'all_docs': parsed_result})
        
        elif analysis_type == 'NER':
            analyzer = EnhancedNERAnalyzer()
            results = {}
            
            # Ensure static directory exists
            os.makedirs(STATIC_FOLDER, exist_ok=True)
            
            for filename, text in texts.items():
                print(f"Processing NER for {filename}")
                result = analyzer.process_text(text, output_dir=STATIC_FOLDER)
                results[filename] = result
            
            return render_template('results.html',
                                 analysis_type='NER',
                                 files=results)
        
        elif analysis_type == 'network':
            analyzer = EnhancedNetworkAnalyzer()
            results = {}
            
            # Ensure static directory exists
            os.makedirs(STATIC_FOLDER, exist_ok=True)
            
            for filename, text in texts.items():
                print(f"Processing network for {filename}")
                result = analyzer.create_network_graph(text, output_dir=STATIC_FOLDER)
                results[filename] = result
            
            return render_template('results.html',
                                 analysis_type='network',
                                 files=results)
        
        else:
            return jsonify({'error': 'Invalid analysis type'}), 400
            
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@text_bp.route('/results')
def results():
    """Display results page (for direct navigation)"""
    return render_template('results.html', 
                         analysis_type='doc2vec',
                         files={})