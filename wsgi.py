from flask import Flask, render_template, request, jsonify
import os
import spacy

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # Reduce to 8MB

# Use md model since we already have it installed
nlp = spacy.load('el_core_news_md')  # Use the model we know exists
# Disable unnecessary components to save memory
nlp.select_pipes(enable=['ner'])  # Only keep NER

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
        
        for file in files:
            if file and file.filename:
                try:
                    full_text = file.read().decode('utf-8')
                    preview = full_text[:500]  # Reduce preview size
                    
                    # Process only first 5000 characters for entities
                    doc = nlp(full_text[:5000])
                    
                    texts[file.filename] = {
                        'preview': preview,
                        'entities': [
                            {'text': ent.text, 'type': ent.label_}
                            for ent in doc.ents
                        ][:50]  # Limit number of entities shown
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
