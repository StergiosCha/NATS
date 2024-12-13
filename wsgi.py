from flask import Flask, render_template, request, jsonify
import os
import spacy
from app.models.ner_analyzer import NERAnalyzer
from app.models.doc_embeddings import DocEmbeddingAnalyzer

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

# Initialize analyzers
ner_analyzer = NERAnalyzer()
doc_analyzer = DocEmbeddingAnalyzer()

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        analysis_type = request.form.get('analysis_type', 'NER')
        reduction_type = request.form.get('reduction_type', 'pca')
        files = request.files.getlist('files')
        texts = {}
        
        os.makedirs('app/static/networks', exist_ok=True)
        
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')
                    
                    if analysis_type == 'NER':
                        result = ner_analyzer.process_text(text, 'app/static/networks')
                    else:  # Doc2Vec
                        result = doc_analyzer.analyze_doc(text, reduction_type)
                    
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
