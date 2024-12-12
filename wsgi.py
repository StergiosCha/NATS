from flask import Flask, render_template, request, jsonify
import os
import spacy
from pyvis.network import Network
from collections import defaultdict

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

nlp = spacy.load('el_core_news_md', disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])

def process_text_in_chunks(text, chunk_size=3000):
    """Process text in chunks to handle large texts"""
    entities_dict = defaultdict(set)
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    for chunk in chunks:
        doc = nlp(chunk)
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
                entities_dict[ent.label_].add(ent.text)
    
    return entities_dict

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
                    full_text = file.read().decode('utf-8')
                    preview = full_text[:200]
                    
                    # Process entire text in chunks
                    entities_by_type = process_text_in_chunks(full_text)
                    
                    # Create network
                    net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
                    
                    # Color scheme for entity types
                    colors = {
                        'PERSON': '#ffff44',  # Yellow
                        'ORG': '#4444ff',     # Blue
                        'LOC': '#44ff44',     # Green
                        'GPE': '#44ff44',     # Green
                        'DATE': '#ff44ff'      # Purple
                    }
                    
                    # Add all entities to network
                    entities_dict = {}
                    for ent_type, entities in entities_by_type.items():
                        for entity in entities:
                            entities_dict[entity] = ent_type
                            net.add_node(entity,
                                       label=entity,
                                       color=colors[ent_type],
                                       title=f"Type: {ent_type}")
                            
                            # Connect entities of same type
                            for other_entity in entities:
                                if entity != other_entity:
                                    net.add_edge(entity, other_entity, color='rgba(255,255,255,0.2)')
                    
                    # Save network file
                    network_filename = f'networks/network_{len(texts)}.html'
                    net.save_graph(f'static/{network_filename}')
                    
                    # Store results
                    texts[file.filename] = {
                        'preview': preview,
                        'entities': entities_dict,
                        'network_path': network_filename,
                        'entity_counts': {label: len(ents) for label, ents in entities_by_type.items()}
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
