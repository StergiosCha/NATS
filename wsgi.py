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
                    
                    console.log('Analysis response:', data);
                    
                    if (data.results) {
                        let plotCount = 0;
                        console.log('Found results, checking for visualizations...');
                        
                        if (data.results.embeddings && data.results.embeddings.plot) {
                            const viz = data.results.embeddings.plot;
                            if (viz.type === 'plotly') {
                                result.innerHTML += '<h4>📊 Document Embeddings Visualization</h4>';
                                result.innerHTML += `<div id="plot-embeddings-${plotCount}" style="width: 100%; height: 600px; margin: 20px 0;"></div>`;
                                try {
                                    Plotly.newPlot(`plot-embeddings-${plotCount}`, viz.data, viz.layout, {responsive: true});
                                    console.log(`✅ Embeddings chart created successfully`);
                                } catch (error) {
                                    console.error('❌ Error creating embeddings chart:', error);
                                }
                                plotCount++;
                            }
                        }
                        
                        if (data.results.network) {
                            Object.keys(data.results.network).forEach(filename => {
                                const networkData = data.results.network[filename];
                                if (networkData.visualizations && networkData.visualizations.network_plot) {
                                    const viz = networkData.visualizations.network_plot;
                                    if (viz.type === 'plotly') {
                                        result.innerHTML += `<h4>🕸️ Network Analysis - ${filename}</h4>`;
                                        result.innerHTML += `<div id="plot-network-${plotCount}" style="width: 100%; height: 600px; margin: 20px 0;"></div>`;
                                        try {
                                            Plotly.newPlot(`plot-network-${plotCount}`, viz.data, viz.layout, {responsive: true});
                                            console.log(`✅ Network chart created successfully`);
                                        } catch (error) {
                                            console.error('❌ Error creating network chart:', error);
                                        }
                                        plotCount++;
                                    }
                                }
                            });
                        }
                        
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
                                        try {
                                            Plotly.newPlot(`plot-entities-${plotCount}`, viz.data, viz.layout, {responsive: true});
                                            console.log(`✅ Entity chart created successfully for entities-${plotCount}`);
                                        } catch (error) {
                                            console.error('❌ Error creating entity chart:', error);
                                        }
                                        plotCount++;
                                    }
                                }
                            });
                        }
                    }
                    
                    if (data.results && data.results.stats) {
                        result.innerHTML += '<h4>📊 Analysis Summary:</h4><pre>' + JSON.stringify(data.results.stats, null, 2) + '</pre>';
                    }
                    
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

