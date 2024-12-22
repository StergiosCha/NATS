from flask import Flask, render_template, request, jsonify
import os
import spacy
from pyvis.network import Network
from collections import Counter
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max file size

# Initialize spaCy
try:
    nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
    nlp.add_pipe('sentencizer')
except Exception as e:
    logger.error(f"Failed to load spaCy model: {e}")
    raise

# Ensure required directories exist
os.makedirs(os.path.join(app.static_folder, 'networks'), exist_ok=True)

def process_text_safely(text):
    """Process text with minimal memory usage"""
    if not text:
        return {}, {}, set()
        
    try:
        entities = {}
        entity_counts = Counter()
        connections = set()
        
        # Process limited text length
        doc = nlp(text[:35000])
        
        # Process entities
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
                entities[ent.text] = ent.label_
                entity_counts[ent.label_] += 1
        
        # Find connections
        for sent in doc.sents:
            sent_ents = [ent for ent in sent.ents if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']]
            for i, ent1 in enumerate(sent_ents):
                for ent2 in sent_ents[i+1:]:
                    connections.add((ent1.text, ent2.text))
        
        return entities, dict(entity_counts), connections
    except Exception as e:
        logger.error(f"Error in process_text_safely: {e}")
        return {}, {}, set()

def process_doc2vec(files, reduction_type='pca'):
    """Process files with Doc2Vec and dimension reduction"""
    documents = []
    filenames = []
    
    for file in files:
        if not file or not file.filename:
            continue
            
        try:
            text = file.read().decode('utf-8')
            if not text.strip():
                continue
                
            doc = nlp(text[:3000])
            tokens = [token.text for token in doc if not token.is_space]
            
            if tokens:  # Only add if we have tokens
                documents.append(TaggedDocument(words=tokens, tags=[file.filename]))
                filenames.append(file.filename)
            
            file.seek(0)  # Reset file pointer
        except Exception as e:
            logger.error(f"Error processing {file.filename} for Doc2Vec: {e}")
            continue

    if not documents:
        return None, None

    try:
        # Train Doc2Vec
        model = Doc2Vec(documents, vector_size=20, min_count=1, epochs=10)
        vectors = [model.dv[fname] for fname in filenames]
        
        # Dimension reduction
        if reduction_type == 'pca':
            reducer = PCA(n_components=2)
        else:
            perplexity = min(3, len(vectors)-1)
            reducer = TSNE(n_components=2, perplexity=perplexity)
            
        coords = reducer.fit_transform(vectors)
        
        # Create plot
        fig = px.scatter(x=coords[:, 0], y=coords[:, 1],
                        text=filenames,
                        title=f"Document Embeddings ({reduction_type.upper()})")
        
        return fig.to_json(), filenames
    except Exception as e:
        logger.error(f"Error in Doc2Vec processing: {e}")
        return None, None

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        if not files or all(not f.filename for f in files):
            return jsonify({'error': 'No valid files provided'}), 400
            
        analysis_type = request.form.get('analysis_type', 'NER')
        texts = {}
        
        if analysis_type == 'NER':
            for file in files:
                if not file or not file.filename:
                    continue
                    
                try:
                    text = file.read().decode('utf-8')
                    if not text.strip():
                        continue
                        
                    # Process text
                    entities, entity_counts, connections = process_text_safely(text)
                    
                    if not entities:  # Skip if no entities found
                        continue
                        
                    # Create network
                    net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
                    
                    # Add nodes with colors
                    for entity, label in entities.items():
                        color = {
                            'PERSON': '#ffff44',
                            'ORG': '#4444ff',
                            'LOC': '#44ff44',
                            'GPE': '#44ff44',
                            'DATE': '#ff44ff'
                        }.get(label, '#ffffff')
                        
                        net.add_node(entity, 
                                   label=entity,
                                   color=color,
                                   title=f"Type: {label}")
                    
                    # Add edges
                    for ent1, ent2 in connections:
                        net.add_edge(ent1, ent2)
                    
                    # Save network
                    network_filename = f'networks/network_{len(texts)}.html'
                    net.save_graph(os.path.join(app.static_folder, network_filename))
                    
                    texts[file.filename] = {
                        'preview': text[:200],
                        'entities': entities,
                        'network_path': network_filename,
                        'entity_counts': entity_counts
                    }
                    
                except Exception as e:
                    logger.error(f"Error processing {file.filename}: {e}")
                    continue
            
            if not texts:
                return jsonify({'error': 'No entities found in any of the provided files'}), 400
                
            return render_template('results.html', 
                                files=texts, 
                                analysis_type='NER')
        
        else:  # Doc2Vec analysis
            reduction_type = request.form.get('reduction_type', 'pca')
            plot_json, filenames = process_doc2vec(files, reduction_type)
            
            if plot_json is None:
                return jsonify({'error': 'No valid documents to process'}), 400
                
            texts['all_docs'] = {
                'plot': plot_json,
                'filenames': filenames,
                'reduction_type': reduction_type
            }
            
            return render_template('results.html',
                                files=texts,
                                analysis_type='Doc2Vec')
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
