from flask import Flask, render_template, request, jsonify
import os
import spacy
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB max

try:
    nlp = spacy.load('el_core_news_md')
except Exception as e:
    print(f"Error loading model: {e}")

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
        
        # Process files
        for file in files:
            if file and file.filename:
                try:
                    full_text = file.read().decode('utf-8')
                    preview = full_text[:500]
                    
                    # Process with spaCy
                    doc = nlp(full_text[:5000])
                    docs[file.filename] = doc
                    
                    # Store results
                    texts[file.filename] = {
                        'preview': preview,
                        'entities': [
                            {'text': ent.text, 'type': ent.label_}
                            for ent in doc.ents
                        ][:50],
                        'similarities': {}  # Initialize empty similarities dict
                    }
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue
        
        # Calculate similarities if we have multiple documents
        if len(docs) > 1:
            doc_names = list(docs.keys())
            for i, name1 in enumerate(doc_names):
                for j, name2 in enumerate(doc_names[i+1:], i+1):
                    sim = docs[name1].similarity(docs[name2])
                    texts[name1]['similarities'][name2] = round(float(sim), 3)
                
        return render_template('results.html', files=texts, has_similarities=len(docs)>1)
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
