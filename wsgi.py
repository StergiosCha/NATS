from flask import Flask, render_template, request, jsonify
import os
import spacy
from app.models.network_analyzer import NetworkAnalyzer

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB max

nlp = spacy.load('el_core_news_md')
nlp.select_pipes(enable=['ner'])  # Only keep NER pipe
network_analyzer = NetworkAnalyzer()

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        texts = {}
        
        # Create static directory if it doesn't exist
        os.makedirs('static/networks', exist_ok=True)
        
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')
                    preview = text[:500]  # Short preview
                    
                    # Create network
                    result = network_analyzer.create_network(text, 'static/networks')
                    
                    texts[file.filename] = {
                        'preview': preview,
                        'network_path': result['network_path'],
                        'entities': result['entities']
                    }
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue
                
        return render_template('results.html', files=texts)
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500
