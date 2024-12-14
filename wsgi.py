from flask import Flask, render_template, request, jsonify
import os
import spacy
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

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

        documents = []
        filenames = []

        for file in files:
            if file and file.filename:
                try:
                    # Try different encodings
                    content = file.read()
                    try:
                        text = content.decode('utf-8-sig')
                    except UnicodeDecodeError:
                        try:
                            text = content.decode('cp1253')
                        except UnicodeDecodeError:
                            text = content.decode('iso-8859-7')
                    
                    doc = nlp(text[:5000])
                    tokens = [token.text for token in doc 
                            if not token.is_punct and not token.is_space]
                    
                    if tokens:
                        documents.append(TaggedDocument(words=tokens, tags=[file.filename]))
                        filenames.append(file.filename)
                        print(f"Successfully processed: {file.filename}")
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue

        if len(documents) < 2:
            return jsonify({'error': f'Need at least 2 documents. Only processed: {len(documents)}'}), 400

        # Train Doc2Vec model
        model = Doc2Vec(documents, vector_size=10, min_count=1, epochs=5, workers=1)
        vectors = np.array([model.dv[fname] for fname in filenames])

        # Dimension reduction
        if reduction_type == 'pca':
            reducer = PCA(n_components=2)
        else:
            reducer = TSNE(n_components=2, perplexity=2)
            
        coords = reducer.fit_transform(vectors)
        
        # Create visualization
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

        return render_template('results.html', files=texts, analysis_type=analysis_type)

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
