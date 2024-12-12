from flask import Flask, render_template, request, jsonify
import os
import spacy
from pyvis.network import Network
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

nlp = spacy.load('el_core_news_md', disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])

def verify_location(name):
    """Verify if a name is actually a location using geocoding"""
    try:
        geolocator = Nominatim(user_agent="nats_verifier")
        location = geolocator.geocode(name, timeout=5)
        return location is not None
    except GeocoderTimedOut:
        return False

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
        
        # Create static/networks directory
        os.makedirs('static/networks', exist_ok=True)
        
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')
                    preview = text[:200]
                    doc = nlp(text[:5000])
                    
                    # Create network
                    net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
                    
                    # Track entities and add to network
                    entities = {}
                    certain_entities = set()
                    uncertain_entities = set()
                    
                    for ent in doc.ents:
                        if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
                            entities[ent.text] = ent.label_
                            
                            # Verify locations
                            is_certain = True
                            if ent.label_ in ['LOC', 'GPE']:
                                is_certain = verify_location(ent.text)
                            
                            if is_certain:
                                certain_entities.add(ent.text)
                                color = '#44ff44'  # Green for verified locations
                                if ent.label_ == 'PERSON':
                                    color = '#ffff44'  # Yellow for people
                                elif ent.label_ == 'ORG':
                                    color = '#4444ff'  # Blue for organizations
                                elif ent.label_ == 'DATE':
                                    color = '#ff44ff'  # Purple for dates
                            else:
                                uncertain_entities.add(ent.text)
                                color = '#ff9900'  # Orange for unverified locations
                                
                            net.add_node(ent.text, 
                                       label=ent.text,
                                       color=color,
                                       title=f"Type: {ent.label_}, Verified: {is_certain}")
                    
                    # Add edges for entities in same sentence
                    for sent in doc.sents:
                        sent_ents = [ent for ent in sent.ents if ent.label_ in entities]
                        for i, ent1 in enumerate(sent_ents):
                            for ent2 in sent_ents[i+1:]:
                                net.add_edge(ent1.text, ent2.text, title=sent.text[:100])
                    
                    # Save network
                    network_filename = f'networks/network_{len(texts)}.html'
                    net.save_graph(f'static/{network_filename}')
                    
                    texts[file.filename] = {
                        'preview': preview,
                        'entities': entities,
                        'network_path': network_filename,
                        'certain_entities': list(certain_entities),
                        'uncertain_entities': list(uncertain_entities)
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
