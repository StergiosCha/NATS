from flask import Flask, render_template, request, jsonify
import os
import spacy
from app.models.ner_analyzer import NERAnalyzer
from app.models.doc_embeddings import DocEmbeddingsAnalyzer
from app.models.word_embeddings import WordEmbeddingsAnalyzer

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max

# Initialize analyzers
ner_analyzer = NERAnalyzer()
doc_analyzer = DocEmbeddingsAnalyzer()
word_analyzer = WordEmbeddingsAnalyzer()

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        analysis_type = request.form.get('analysis_type', 'NER')
        files = request.files.getlist('files')
        texts = {}
        
        # Process files based on analysis type
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')
                    
                    if analysis_type == 'NER':
                        result = ner_analyzer.process_text(text, 'app/static/networks')
                    elif analysis_type == 'Doc2Vec':
                        result = doc_analyzer.analyze_text(text)
                    else:  # Word2Vec
                        result = word_analyzer.analyze_text(text)
                    
                    texts[file.filename] = result
                    
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue
                
        return render_template('results.html', 
                             files=texts, 
                             analysis_type=analysis_type)
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
