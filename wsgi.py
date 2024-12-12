from flask import Flask, render_template, request, jsonify
import os
import spacy
from pyvis.network import Network
from collections import Counter

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
nlp.add_pipe('sentencizer')

def process_text_chunks(text, chunk_size=5000):
    """Process text in chunks and collect all entities and connections"""
    entities = {}
    entity_counts = Counter()
    connections = set()  # Store unique connections
    
    # Process text in chunks
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        doc = nlp(chunk)
        
        # Process entities in this chunk
        chunk_entities = {}
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
                entities[ent.text] = ent.label_
                chunk_entities[ent.text] = ent.label_
                entity_counts[ent.label_] += 1
        
        # Find connections in sentences
        for sent in doc.sents:
            sent_ents = [ent for ent in sent.ents if ent.text in chunk_entities]
            for i, ent1 in enumerate(sent_ents):
                for ent2 in sent_ents[i+1:]:
                    connections.add((ent1.text, ent2.text, sent.text[:100]))
    
    return entities, dict(entity_counts), connections

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
        
        os.makedirs('static/networks', exist_ok=True)
        
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')
                    
                    # Process entire text in chunks
                    entities, entity_counts, connections = process_text_chunks(text)
                    
                    # Create network
                    net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
                    
                    # Add nodes
                    for entity, label in entities.items():
                        color = {
                            'PERSON': '#ffff44',  # Yellow
                            'ORG': '#4444ff',     # Blue
                            'LOC': '#44ff44',     # Green
                            'GPE': '#44ff44',     # Green
                            'DATE': '#ff44ff'     # Purple
                        }.get(label, '#ffffff')
                        
                        net.add_node(entity, 
                                   label=entity,
                                   color=color,
                                   title=f"Type: {label}")
                    
                    # Add all connections
                    for ent1, ent2, context in connections:
                        net.add_edge(ent1, ent2, title=context)
                    
                    # Save network
                    network_filename = f'networks/network_{len(texts)}.html'
                    net.save_graph(f'static/{network_filename}')
                    
                    texts[file.filename] = {
                        'preview': text[:200],
                        'entities': entities,
                        'network_path': network_filename,
                        'entity_counts': entity_counts
                    }
                    
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue
                
        return render_template('results.html', files=texts)
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
