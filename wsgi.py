from flask import Flask, render_template, request, jsonify
import os
import spacy
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

try:
    nlp = spacy.load('el_core_news_md')
    logging.info("Successfully loaded spaCy model")
except Exception as e:
    logging.error(f"Failed to load spaCy model: {str(e)}")

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        logging.info("Starting file upload process")
        if 'files' not in request.files:
            logging.warning("No files in request")
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        texts = {}
        
        for file in files:
            if file and file.filename:
                try:
                    logging.info(f"Processing file: {file.filename}")
                    text = file.read().decode('utf-8')
                    texts[file.filename] = text[:1000]  # Back to simple version
                except Exception as e:
                    logging.error(f"Error processing {file.filename}: {str(e)}")
                    continue
                
        return render_template('results.html', files=texts)
    
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return jsonify({'error': f"Upload failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run()
