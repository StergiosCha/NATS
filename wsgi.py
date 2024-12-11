from flask import Flask, render_template, request, jsonify
import os
import spacy
from app.models.doc_embeddings import DocEmbeddingsAnalyzer

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

nlp = spacy.load('el_core_news_md')

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
        
        # Process files with spaCy
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')
                    doc = nlp(text)
                    texts[file.filename] = {
                        'text': text[:1000],  # Preview
                        'doc': doc  # SpaCy doc for analysis
                    }
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue
        
        if len(texts) < 2:
            return render_template('upload.html', 
                                error="Please upload at least 2 files for analysis")
        
        # Perform document embeddings analysis
        analyzer = DocEmbeddingsAnalyzer()
        processed_docs = {name: data['doc'] for name, data in texts.items()}
        embeddings = analyzer.create_embeddings(processed_docs)
        
        return render_template('results.html', 
                             files=texts,
                             embeddings=embeddings)
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run()
