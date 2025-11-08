#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import json
from werkzeug.utils import secure_filename

# Import our enhanced analyzers
from app.models.doc_embeddings import EnhancedDocEmbeddingAnalyzer
from app.models.ner_analyzer import EnhancedNERAnalyzer
from app.models.network_analyzer import EnhancedNetworkAnalyzer

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize analyzers
doc_analyzer = EnhancedDocEmbeddingAnalyzer()
ner_analyzer = EnhancedNERAnalyzer()
network_analyzer = EnhancedNetworkAnalyzer()

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
os.makedirs('static/networks', exist_ok=True)

@app.route('/test')
def test_viz():
    return send_from_directory('.', 'test_viz.html')

@app.route('/simple')
def simple_test():
    return send_from_directory('.', 'simple_test.html')

@app.route('/')
def home():
    return send_from_directory('frontend/build', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('frontend/build/static', filename)

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('frontend/build', 'manifest.json')

@app.route('/favicon.ico')
def serve_favicon():
    return send_from_directory('frontend/build', 'favicon.ico')

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'NATS'})

@app.route('/api/analyze', methods=['POST'])
def analyze_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        analysis_type = request.form.get('analysis_type', 'enhanced_ner')
        embedding_type = request.form.get('embedding_type', 'sentence_transformer')
        reduction_method = request.form.get('reduction_method', 'pca')

        analysis_id = str(uuid.uuid4())
        
        texts = {}
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')
                    texts[secure_filename(file.filename)] = text
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue
        
        if not texts:
            return jsonify({'error': 'No valid text files uploaded'}), 400

        results = {}
        
        if analysis_type == 'enhanced_ner' or analysis_type == 'comprehensive':
            ner_results = {}
            for filename, text in texts.items():
                result = ner_analyzer.process_text(text, 'static/networks')
                ner_results[filename] = result
            results['entities'] = ner_results

        if analysis_type == 'enhanced_embeddings' or analysis_type == 'comprehensive':
            embeddings_result = doc_analyzer.create_comprehensive_visualization(
                texts, embedding_type, reduction_method
            )
            # Flatten embeddings result to top level
            if 'scatter_plot' in embeddings_result:
                results['scatter_plot'] = embeddings_result['scatter_plot']
            if 'features_chart' in embeddings_result:
                results['features_chart'] = embeddings_result['features_chart']
            if 'similarity_heatmap' in embeddings_result:
                results['similarity_heatmap'] = embeddings_result['similarity_heatmap']
            if 'clusters' in embeddings_result:
                results['clusters'] = embeddings_result['clusters']
            results['embeddings'] = embeddings_result

        if analysis_type == 'enhanced_network' or analysis_type == 'comprehensive':
            network_results = {}
            for filename, text in texts.items():
                result = network_analyzer.create_network(text, 'static/networks')
                network_results[filename] = result
            results['network'] = network_results

        stats = {
            'total_documents': len(texts),
            'total_entities': sum(len(r.get('entities', {})) for r in results.get('entities', {}).values()),
            'num_communities': len(set().union(*[r.get('communities', {}).values() for r in results.get('network', {}).values()])),
            'avg_degree': 0
        }
        
        if results.get('network'):
            all_centrality = []
            for r in results['network'].values():
                if 'centrality' in r:
                    all_centrality.extend([c['degree'] for c in r['centrality'].values()])
            if all_centrality:
                stats['avg_degree'] = sum(all_centrality) / len(all_centrality)

        results['stats'] = stats
        results['analysis_id'] = analysis_id
        results['analysis_type'] = analysis_type

        def convert_plotly_in_dict(d):
            if isinstance(d, dict):
                for key, value in d.items():
                    if isinstance(value, dict) and 'type' in value and value['type'] == 'plotly':
                        if 'data' in value and hasattr(value['data'], 'to_json'):
                            value['data'] = json.loads(value['data'].to_json())
                        if 'layout' in value and hasattr(value['layout'], 'to_json'):
                            value['layout'] = json.loads(value['layout'].to_json())
                    else:
                        convert_plotly_in_dict(value)
            elif isinstance(d, list):
                for item in d:
                    convert_plotly_in_dict(item)
        
        convert_plotly_in_dict(results)

        results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{analysis_id}.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return jsonify({'analysis_id': analysis_id, 'results': results})

    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/results/<analysis_id>', methods=['GET'])
def get_results(analysis_id):
    try:
        results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{analysis_id}.json')
        if not os.path.exists(results_path):
            return jsonify({'error': 'Analysis not found'}), 404
        
        with open(results_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<analysis_id>', methods=['GET'])
def download_results(analysis_id):
    try:
        format_type = request.args.get('format', 'json')
        results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{analysis_id}.json')
        
        if not os.path.exists(results_path):
            return jsonify({'error': 'Analysis not found'}), 404
        
        if format_type == 'json':
            return send_from_directory(app.config['RESULTS_FOLDER'], f'{analysis_id}.json', as_attachment=True)
        else:
            return jsonify({'error': 'Only JSON format supported'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

