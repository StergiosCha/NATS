from flask import Flask, render_template, request, jsonify
import os
import spacy
from pyvis.network import Network
from collections import Counter

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
nlp.add_pipe('sentencizer')

def process_text_safely(text):
    """Process text with minimal memory usage"""
    entities = {}
    entity_counts = Counter()
    connections = set()
    
    # Only process first 10000 characters for now
    doc = nlp(text[:25000])
    
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
                    
                    # Process text
                    entities, entity_counts, connections = process_text_safely(text)
                    
                    # Create network
                    net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
                    
                    # Add nodes with colors
                    for entity, label in entities.items():
                        color = '#ffffff'  # default white
                        if label == 'PERSON':
                            color = '#ffff44'  # yellow
                        elif label == 'ORG':
                            color = '#4444ff'  # blue
                        elif label in ['LOC', 'GPE']:
                            color = '#44ff44'  # green
                        elif label == 'DATE':
                            color = '#ff44ff'  # purple
                            
                        net.add_node(entity, 
                                   label=entity,
                                   color=color,
                                   title=f"Type: {label}")
                    
                    # Add edges
                    for ent1, ent2 in connections:
                        net.add_edge(ent1, ent2)
                    
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
