from flask import Flask, render_template, request, jsonify
import os
import spacy
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Load spaCy with minimal components
nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        print("Starting file upload process")  # Debug print
        
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        analysis_type = request.form.get('analysis_type', 'NER')
        
        print(f"Analysis type: {analysis_type}")  # Debug print
        
        if analysis_type == 'NER':
            # Just return empty results for now to test
            return render_template('results.html', 
                                 files={}, 
                                 analysis_type='NER')
                                 
        # If we get here, it's Doc2Vec analysis
        reduction_type = request.form.get('reduction_type', 'pca')
        print(f"Reduction type: {reduction_type}")  # Debug print

        # Process files and create visualization
        # ... rest of your Doc2Vec code ...

    except Exception as e:
        print(f"Error in upload_files: {str(e)}")  # Debug print
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
