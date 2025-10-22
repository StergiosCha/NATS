#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import json
from werkzeug.utils import secure_filename
import plotly

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
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
os.makedirs('static/networks', exist_ok=True)

def convert_plotly_to_json(obj):
    """Convert Plotly objects to JSON-serializable format"""
    if hasattr(obj, 'to_json'):
        return json.loads(obj.to_json())
    elif hasattr(obj, 'data') and hasattr(obj, 'layout'):
        return {
            'data': json.loads(obj.data.to_json()),
            'layout': json.loads(obj.layout.to_json())
        }
    return obj

@app.route('/test')
def test_viz():
    """Test visualization page"""
    return send_from_directory('.', 'test_viz.html')

@app.route('/')
def home():
    """Serve simple dashboard"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NATS - Text Analysis Suite</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; border-radius: 10px; }
        .upload-area:hover { border-color: #007bff; background: #f8f9fa; }
        input[type="file"] { margin: 10px 0; }
        select, button { padding: 10px; margin: 10px 0; width: 100%; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #007bff; color: white; border: none; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        button:disabled { background: #6c757d; cursor: not-allowed; }
        .file-item { background: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 5px; }
        .loading { display: none; text-align: center; margin: 20px 0; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #007bff; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .result { display: none; margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
        .result h3 { color: #28a745; margin-top: 0; }
        .result h4 { color: #007bff; margin-top: 20px; }
        pre { background: #e9ecef; padding: 15px; border-radius: 5px; overflow-x: auto; }
        details { margin: 10px 0; }
        summary { cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 NATS - Text Analysis Suite</h1>
        
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="upload-area">
                <input type="file" id="fileInput" name="files" multiple accept=".txt" required>
                <p>Select one or more .txt files to analyze</p>
            </div>
            
            <div id="fileList"></div>
            
            <select id="analysisType" name="analysis_type" required>
                <option value="enhanced_ner">🏷️ Enhanced NER Analysis</option>
                <option value="enhanced_embeddings">📊 Document Embeddings</option>
                <option value="enhanced_network">🕸️ Network Analysis</option>
                <option value="comprehensive">🎯 Comprehensive Analysis</option>
            </select>
            
            <div id="embeddingOptions" style="display: none;">
                <select id="embeddingType" name="embedding_type">
                    <option value="sentence_transformer">Sentence Transformers</option>
                    <option value="doc2vec">Doc2Vec</option>
                </select>
                
                <select id="reductionMethod" name="reduction_method">
                    <option value="pca">PCA</option>
                    <option value="tsne">t-SNE</option>
                    <option value="umap">UMAP</option>
                </select>
            </div>
            
            <button type="submit" id="submitBtn">🔍 Start Analysis</button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Analyzing your text files...</p>
        </div>
        
        <div class="result" id="result"></div>
    </div>

    <script>
        let selectedFiles = [];
        
        document.getElementById('fileInput').addEventListener('change', function(e) {
            selectedFiles = Array.from(e.target.files).filter(file => file.name.endsWith('.txt'));
            displayFiles();
        });
        
        function displayFiles() {
            const fileList = document.getElementById('fileList');
            fileList.innerHTML = '';
            selectedFiles.forEach(file => {
                const div = document.createElement('div');
                div.className = 'file-item';
                div.innerHTML = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
                fileList.appendChild(div);
            });
        }
        
        document.getElementById('analysisType').addEventListener('change', function() {
            const isEmbedding = this.value === 'enhanced_embeddings' || this.value === 'comprehensive';
            document.getElementById('embeddingOptions').style.display = isEmbedding ? 'block' : 'none';
        });
        
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (selectedFiles.length === 0) {
                alert('Please select at least one file');
                return;
            }
            
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            
            submitBtn.disabled = true;
            loading.style.display = 'block';
            result.style.display = 'none';
            
            const formData = new FormData();
            selectedFiles.forEach(file => {
                formData.append('files', file);
            });
            formData.append('analysis_type', document.getElementById('analysisType').value);
            formData.append('embedding_type', document.getElementById('embeddingType').value);
            formData.append('reduction_method', document.getElementById('reductionMethod').value);
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    result.innerHTML = '<h3>✅ Analysis Complete!</h3>';
                    
                    // Debug: Log the response data
                    console.log('Analysis response:', data);
                    
                    // Display visualizations from results
                    if (data.results) {
                        let plotCount = 0;
                        console.log('Found results, checking for visualizations...');
                        
                        // Check for embeddings visualization
                        if (data.results.embeddings && data.results.embeddings.plot) {
                            const viz = data.results.embeddings.plot;
                            if (viz.type === 'plotly') {
                                result.innerHTML += '<h4>📊 Document Embeddings Visualization</h4>';
                                result.innerHTML += `<div id="plot-embeddings-${plotCount}" style="width: 100%; height: 600px; margin: 20px 0;"></div>`;
                                setTimeout(() => {
                                    Plotly.newPlot(`plot-embeddings-${plotCount}`, viz.data, viz.layout, {responsive: true});
                                }, 100);
                                plotCount++;
                            }
                        }
                        
                        // Check for network visualizations
                        if (data.results.network) {
                            Object.keys(data.results.network).forEach(filename => {
                                const networkData = data.results.network[filename];
                                if (networkData.visualizations && networkData.visualizations.network_plot) {
                                    const viz = networkData.visualizations.network_plot;
                                    if (viz.type === 'plotly') {
                                        result.innerHTML += `<h4>🕸️ Network Analysis - ${filename}</h4>`;
                                        result.innerHTML += `<div id="plot-network-${plotCount}" style="width: 100%; height: 600px; margin: 20px 0;"></div>`;
                                        setTimeout(() => {
                                            Plotly.newPlot(`plot-network-${plotCount}`, viz.data, viz.layout, {responsive: true});
                                        }, 100);
                                        plotCount++;
                                    }
                                }
                            });
                        }
                        
                        // Check for entity visualizations
                        if (data.results.entities) {
                            console.log('Found entities, checking for visualizations...');
                            Object.keys(data.results.entities).forEach(filename => {
                                const entityData = data.results.entities[filename];
                                console.log(`Checking entity data for ${filename}:`, entityData);
                                if (entityData.visualizations && entityData.visualizations.entity_plot) {
                                    const viz = entityData.visualizations.entity_plot;
                                    console.log(`Found entity plot for ${filename}:`, viz);
                                    if (viz.type === 'plotly') {
                                        result.innerHTML += `<h4>🏷️ Entity Analysis - ${filename}</h4>`;
                                        result.innerHTML += `<div id="plot-entities-${plotCount}" style="width: 100%; height: 600px; margin: 20px 0;"></div>`;
                                        console.log(`Creating Plotly chart for entities-${plotCount}`);
                                        setTimeout(() => {
                                            try {
                                                Plotly.newPlot(`plot-entities-${plotCount}`, viz.data, viz.layout, {responsive: true});
                                                console.log(`Plotly chart created successfully for entities-${plotCount}`);
                                            } catch (error) {
                                                console.error('Error creating Plotly chart:', error);
                                            }
                                        }, 100);
                                        plotCount++;
                                    }
                                }
                            });
                        }
                    }
                    
                    // Display summary data
                    if (data.results && data.results.stats) {
                        result.innerHTML += '<h4>📊 Analysis Summary:</h4><pre>' + JSON.stringify(data.results.stats, null, 2) + '</pre>';
                    }
                    
                    // Display full results (collapsed by default)
                    result.innerHTML += '<details><summary>📋 Full Results (Click to expand)</summary><pre>' + JSON.stringify(data, null, 2) + '</pre></details>';
                    result.style.display = 'block';
                } else {
                    result.innerHTML = '<h3>❌ Error:</h3><p>' + data.error + '</p>';
                    result.style.display = 'block';
                }
            } catch (error) {
                result.innerHTML = '<h3>❌ Error:</h3><p>' + error.message + '</p>';
                result.style.display = 'block';
            } finally {
                submitBtn.disabled = false;
                loading.style.display = 'none';
            }
        });
    </script>
</body>
</html>
    '''

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('frontend/build/static', filename)

@app.route('/static/css/<filename>')
def serve_css(filename):
    """Serve CSS files"""
    return send_from_directory('frontend/build/static/css', filename)

@app.route('/static/js/<filename>')
def serve_js(filename):
    """Serve JS files"""
    return send_from_directory('frontend/build/static/js', filename)

@app.route('/manifest.json')
def serve_manifest():
    """Serve manifest.json"""
    return send_from_directory('frontend/build', 'manifest.json')

@app.route('/favicon.ico')
def serve_favicon():
    """Serve favicon"""
    return send_from_directory('frontend/build', 'favicon.ico')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'NATS'})

@app.route('/api/analyze', methods=['POST'])
def analyze_files():
    """Enhanced analysis endpoint"""
try:
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
        analysis_type = request.form.get('analysis_type', 'enhanced_ner')
        embedding_type = request.form.get('embedding_type', 'sentence_transformer')
        reduction_method = request.form.get('reduction_method', 'pca')

        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
       
        # Process files
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

        # Perform analysis based on type
        results = {}
        
        if analysis_type == 'enhanced_ner' or analysis_type == 'comprehensive':
            ner_results = {}
            for filename, text in texts.items():
                result = ner_analyzer.create_enhanced_network(text, 'static/networks')
                ner_results[filename] = result
            results['entities'] = ner_results

        if analysis_type == 'enhanced_embeddings' or analysis_type == 'comprehensive':
            embeddings_result = doc_analyzer.create_comprehensive_visualization(
                texts, embedding_type, reduction_method
            )
            results['embeddings'] = embeddings_result

        if analysis_type == 'enhanced_network' or analysis_type == 'comprehensive':
            network_results = {}
            for filename, text in texts.items():
                result = network_analyzer.create_enhanced_network(text, 'static/networks')
                network_results[filename] = result
            results['network'] = network_results

        # Calculate overall stats
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

        # Convert Plotly objects to JSON-serializable format
        def convert_plotly_in_dict(d):
            if isinstance(d, dict):
                for key, value in d.items():
                    if isinstance(value, dict) and 'type' in value and value['type'] == 'plotly':
                        # Convert Plotly data and layout
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

        # Save results
        results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{analysis_id}.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return jsonify({'analysis_id': analysis_id, 'results': results})

    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/results/<analysis_id>')
def get_results(analysis_id):
    """Get analysis results by ID"""
    try:
        results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{analysis_id}.json')
        
        if not os.path.exists(results_path):
            return jsonify({'error': 'Results not found'}), 404
        
        with open(results_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        return jsonify(results)
    
                except Exception as e:
        return jsonify({'error': f'Failed to load results: {str(e)}'}), 500

@app.route('/api/download/<analysis_id>')
def download_results(analysis_id):
    """Download analysis results"""
    try:
        results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{analysis_id}.json')
        
        if not os.path.exists(results_path):
            return jsonify({'error': 'Results not found'}), 404
        
        format_type = request.args.get('format', 'json')
        
        if format_type == 'json':
            with open(results_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        
        elif format_type == 'csv':
            with open(results_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            csv_data = "Entity,Type,Importance\n"
            
            # Extract entities from all files
            for filename, file_data in data.get('entities', {}).items():
                entities = file_data.get('entities', {})
                for entity, entity_type in entities.items():
                    importance = data.get('importance_scores', {}).get(entity, 0)
                    csv_data += f'"{entity}","{entity_type}",{importance}\n'
            
            return csv_data, 200, {'Content-Type': 'text/csv'}
        
        return jsonify({'error': 'Unsupported format'}), 400
   
except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))