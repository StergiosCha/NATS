from flask import Flask, render_template, request, jsonify
import os
import spacy
from pyvis.network import Network
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Load spaCy with minimal components
nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
nlp.add_pipe('sentencizer')

def process_ner(files):
    texts = {}
    os.makedirs('app/static/networks', exist_ok=True)
    
    for file in files:
        if file and file.filename:
            try:
                text = file.read().decode('utf-8')
                doc = nlp(text[:5000])
                
                # Create network
                net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
                
                entities = {}
                for ent in doc.ents:
                    if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
                        entities[ent.text] = ent.label_
                
                # Add nodes with colors
                for entity, type_ in entities.items():
                    color = '#ffffff'
                    if type_ == 'PERSON':
                        color = '#ffff44'
                    elif type_ == 'ORG':
                        color = '#4444ff'
                    elif type_ in ['LOC', 'GPE']:
                        color = '#44ff44'
                    elif type_ == 'DATE':
                        color = '#ff44ff'
                        
                    net.add_node(entity, 
                               label=entity,
                               color=color,
                               title=f"Type: {type_}")
                
                # Add edges
                for sent in doc.sents:
                    sent_ents = [ent for ent in sent.ents if ent.text in entities]
                    for i, ent1 in enumerate(sent_ents):
                        for ent2 in sent_ents[i+1:]:
                            net.add_edge(ent1.text, ent2.text)
                
                # Save network
                network_filename = f'networks/network_{len(texts)}.html'
                net.save_graph(f'static/{network_filename}')
                
                texts[file.filename] = {
                    'network_path': network_filename
                }
                
            except Exception as e:
                print(f"Error processing {file.filename}: {str(e)}")
                continue
    
    return render_template('results.html', files=texts, analysis_type='NER')

def process_embeddings(files, reduction_type='pca'):
    documents = []
    filenames = []
    
    for file in files:
        if file and file.filename:
            try:
                text = file.read().decode('utf-8')
                doc = nlp(text[:3000])  # Process smaller chunk
                tokens = [token.text for token in doc 
                         if not token.is_punct and not token.is_space]
                
                if tokens:
                    documents.append(TaggedDocument(words=tokens, tags=[file.filename]))
                    filenames.append(file.filename)
            except Exception as e:
                print(f"Error processing {file.filename}: {str(e)}")
                continue

    if len(documents) < 2:
        return jsonify({'error': 'Need at least 2 documents'}), 400

    # Train Doc2Vec with minimal parameters
    model = Doc2Vec(documents, vector_size=10, min_count=1, epochs=5, workers=1)
    vectors = np.array([model.dv[fname] for fname in filenames])

    # Dimension reduction
    if reduction_type == 'pca':
        reducer = PCA(n_components=2)
    else:
        reducer = TSNE(n_components=2, perplexity=2)
        
    coords = reducer.fit_transform(vectors)
    
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
                         analysis_type='Doc2Vec',
                         reduction_type=reduction_type)

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
        
        if analysis_type == 'NER':
            return process_ner(files)
        else:
            reduction_type = request.form.get('reduction_type', 'pca')
            return process_embeddings(files, reduction_type)
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
