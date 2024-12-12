from flask import Flask, render_template, request, jsonify
import os
import spacy
from pyvis.network import Network

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])

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
        
        # Ensure directory exists
        os.makedirs('static/networks', exist_ok=True)
        
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')
                    doc = nlp(text[:5000])
                    
                    # Create network
                    net = Network(height='500px', width='100%')
                    
                    # Process entities
                    for ent in doc.ents:
                        if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
                            net.add_node(ent.text, 
                                       title=ent.label_)
                    
                    # Save network
                    net_file = f'network_{len(texts)}.html'
                    net.save_graph(f'static/networks/{net_file}')
                    
                    texts[file.filename] = {
                        'preview': text[:200],
                        'network_file': f'networks/{net_file}'
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
