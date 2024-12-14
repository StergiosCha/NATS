from flask import Flask, render_template, request, jsonify
import os
import spacy
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # Reduce to 1MB

# Load spaCy with bare minimum components
nlp = spacy.load('el_core_news_md', disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])

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
        reduction_type = request.form.get('reduction_type', 'pca')
        
        # Collect all documents first
        documents = []
        filenames = []
        
        # Process smaller chunks
        chunk_size = 1000  # Reduced from 3000

        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')[:chunk_size]
                    doc = nlp(text)
                    documents.append(TaggedDocument(
                        words=[token.text for token in doc if not token.is_punct and not token.is_space],
                        tags=[file.filename]
                    ))
                    filenames.append(file.filename)
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue

        if len(documents) < 2:
            return jsonify({'error': 'Need at least 2 documents for comparison'}), 400

        # Train Doc2Vec with minimal parameters
        model = Doc2Vec(documents, vector_size=10, window=5, min_count=1, epochs=5, workers=1)
        
        # Get vectors
        vectors = np.array([model.dv[fname] for fname in filenames])
        
        # Dimension reduction
        if reduction_type == 'pca':
            reducer = PCA(n_components=2)
        else:
            perplexity = min(len(vectors) - 1, 5)  # Reduced perplexity
            reducer = TSNE(n_components=2, perplexity=perplexity, n_iter=250)
            
        coords = reducer.fit_transform(vectors)
        
        # Create simple plot
        fig = px.scatter(x=coords[:, 0], y=coords[:, 1], 
                        text=filenames,
                        title=f"Document Embeddings ({reduction_type.upper()})")
        fig.update_traces(textposition='top center')
        
        texts = {
            'all_docs': {
                'plot': fig.to_json(),
                'reduction_type': reduction_type
            }
        }
        
        return render_template('results.html', 
                             files=texts, 
                             analysis_type=analysis_type)
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
