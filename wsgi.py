# wsgi.py
from flask import Flask, render_template, request, jsonify
import os
import spacy
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
from sklearn.decomposition import PCA
import plotly.express as px

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

# Load spaCy with minimal components
nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        analysis_type = request.form.get('analysis_type', 'NER')
        texts = {}
        
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')[:3000]  # Very limited text size
                    doc = nlp(text)
                    
                    # For Doc2Vec analysis
                    document = TaggedDocument(words=[token.text for token in doc], tags=[file.filename])
                    model = Doc2Vec([document], vector_size=20, min_count=1, epochs=10)  # Minimal parameters
                    doc_vector = model.dv[file.filename]
                    
                    # Simple 2D reduction
                    pca = PCA(n_components=2)
                    coords = pca.fit_transform([doc_vector])
                    
                    fig = px.scatter(x=[coords[0][0]], y=[coords[0][1]], text=[file.filename])
                    
                    texts[file.filename] = {
                        'plot': fig.to_json()
                    }
                    
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue
                
        return render_template('results.html', 
                             files=texts, 
                             analysis_type='Doc2Vec')
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
