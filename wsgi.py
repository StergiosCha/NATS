from flask import Flask, render_template, request, jsonify
import os
import spacy
from pyvis.network import Network

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # Reduce to 4MB max

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
        texts = {}
        
        # Create static/networks directory if it doesn't exist
        os.makedirs('static/networks', exist_ok=True)
        
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')[:3000]
                    preview = text[:200]
                    
                    doc = nlp(text)
                    entities_dict = {}
                    
                    # Create network
                    net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
                    
                    # Add entities to both dictionary and network
                    for ent in doc.ents:
                        if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
                            entities_dict[ent.text] = ent.label_
                            net.add_node(ent.text, 
                                       label=ent.text,
                                       color='#44ff44' if ent.label_ in ['LOC', 'GPE'] else '#ffff44',
                                       title=f"Type: {ent.label_}")
                    
                    # Save network file
                    network_filename = f'networks/network_{len(texts)}.html'
                    net.save_graph(f'static/{network_filename}')
                    
                    texts[file.filename] = {
                        'preview': preview,
                        'entities': entities_dict,
                        'network_path': network_filename
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
