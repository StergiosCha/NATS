from flask import Flask, render_template, request, jsonify
import os
import spacy
from app.models.network_analyzer import NetworkAnalyzer

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB max

nlp = spacy.load('el_core_news_md')
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
        docs = {}
        
        os.makedirs('static/networks', exist_ok=True)
        
        for file in files:
            if file and file.filename:
                try:
                    full_text = file.read().decode('utf-8')
                    preview = full_text[:500]
                    doc = nlp(full_text[:5000])
                    docs[file.filename] = doc
                    
                    # Create network
                    network_result = network_analyzer.create_network(full_text, 'static/networks')
                    
                    texts[file.filename] = {
                        'preview': preview,
                        'entities': [
                            {'text': ent.text, 'type': ent.label_}
                            for ent in doc.ents
                        ][:50],
                        'network_path': network_result['network_path'],
                        'certain_entities': network_result['certain_entities'],
                        'uncertain_entities': network_result['uncertain_entities']
                    }
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue
        
        # Calculate similarities if we have multiple documents
        if len(docs) > 1:
            similarities = {}
            doc_names = list(docs.keys())
            
            for i, name1 in enumerate(doc_names):
                similarities[name1] = {}
                for name2 in doc_names[i+1:]:
                    sim = docs[name1].similarity(docs[name2])
                    similarities[name1][name2] = round(sim, 3)
                    
            for filename in texts:
                texts[filename]['similarities'] = similarities.get(filename, {})
                
        return render_template('results.html', files=texts, has_similarities=len(docs)>1)
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500
