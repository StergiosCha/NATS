from flask import Flask, render_template, request, jsonify
import os
import spacy

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
        texts = {}  # Dictionary, not list
        
        os.makedirs('static/networks', exist_ok=True)
        
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')[:3000]  # Only first 3000 chars
                    preview = text[:200]  # Shorter preview
                    
                    doc = nlp(text)
                    entities_dict = {}  # Create a dictionary instead of list
                    for ent in doc.ents:
                        if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
                            entities_dict[ent.text] = ent.label_
                    
                    texts[file.filename] = {
                        'preview': preview,
                        'entities': entities_dict  # Pass as dictionary
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
