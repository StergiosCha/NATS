from flask import Flask, render_template, request, jsonify
import os
import spacy
from pyvis.network import Network
from collections import Counter

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
nlp.add_pipe('sentencizer')

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
                    doc = nlp(text[:5000])
                    
                    # Create network
                    net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
                    
                    # Process entities and add nodes
                    entities = {}
                    entity_counts = Counter()
                    
                    for ent in doc.ents:
                        if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
                            entities[ent.text] = ent.label_
                            entity_counts[ent.label_] += 1
                            
                            color = {
                                'PERSON': '#ffff44',  # Yellow
                                'ORG': '#4444ff',     # Blue
                                'LOC': '#44ff44',     # Green
                                'GPE': '#44ff44',     # Green
                                'DATE': '#ff44ff'     # Purple
                            }.get(ent.label_, '#ffffff')
                            
                            net.add_node(ent.text, 
                                       label=ent.text,
                                       color=color,
                                       title=f"Type: {ent.label_}")
                    
                    # Add edges between entities in same sentence
                    for sent in doc.sents:
                        sent_ents = [ent for ent in sent.ents if ent.label_ in entities]
                        for i, ent1 in enumerate(sent_ents):
                            for ent2 in sent_ents[i+1:]:
                                net.add_edge(ent1.text, ent2.text, title=sent.text[:100])
                    
                    # Save network
                    network_filename = f'networks/network_{len(texts)}.html'
                    net.save_graph(f'static/{network_filename}')
                    
                    texts[file.filename] = {
                        'preview': text[:200],
                        'entities': entities,
                        'network_path': network_filename,
                        'entity_counts': dict(entity_counts)  # Add entity counts
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
