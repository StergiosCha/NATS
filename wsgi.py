from flask import Flask, render_template, request, jsonify
import os
import spacy
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px
from collections import Counter

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Increased to 16 MB

nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])

def process_text_safely(text):
    entities = {}
    connections = set()
    doc = nlp(text[:35000])
    
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
            entities[ent.text] = ent.label_
    
    for sent in doc.sents:
        sent_ents = [ent for ent in sent.ents if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']]
        for i, ent1 in enumerate(sent_ents):
            for ent2 in sent_ents[i+1:]:
                connections.add((ent1.text, ent2.text))
    
    return entities, connections

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
        texts = {}

        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')[:3000]
                    entities, connections = process_text_safely(text)
                    entity_counts = Counter(entities.values())
                    
                    doc = nlp(text)
                    documents.append(TaggedDocument(words=[token.text for token in doc], tags=[file.filename]))
                    filenames.append(file.filename)
                    
                    texts[file.filename] = {
                        'preview': text[:200],
                        'entities': entities,
                        'entity_counts': dict(entity_counts),
                        'connections': list(connections)
                    }
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")

        model = Doc2Vec(documents, vector_size=20, min_count=1, epochs=10)
        vectors = [model.dv[fname] for fname in filenames]

        if reduction_type == 'pca':
            reducer = PCA(n_components=2)
        else:
            reducer = TSNE(n_components=2, perplexity=min(30, len(vectors)-1))
        coords = reducer.fit_transform(vectors)

        fig = px.scatter(x=coords[:, 0], y=coords[:, 1],
                         text=filenames,
                         title=f"Document Embeddings ({reduction_type.upper()})")

        texts['all_docs'] = {
            'plot': fig.to_json(),
            'reduction_type': reduction_type
        }

        return render_template('results.html', files=texts, analysis_type=analysis_type)
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return "File Too Large", 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
