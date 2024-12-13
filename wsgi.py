# wsgi.py
from flask import Flask, render_template, request, jsonify
import os
import spacy
from app.models.ner_analyzer import NERAnalyzer

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Reduce to 2MB

# Initialize only NER for now
ner_analyzer = NERAnalyzer()

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
        
        os.makedirs('app/static/networks', exist_ok=True)
        
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')
                    result = ner_analyzer.process_text(text, 'app/static/networks')
                    texts[file.filename] = result
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue
                
        return render_template('results.html', 
                             files=texts, 
                             analysis_type='NER')
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
