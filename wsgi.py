# wsgi.py
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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
                # Check file size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                if file_size > app.config['MAX_CONTENT_LENGTH']:
                    return jsonify({'error': f'File {file.filename} exceeds size limit of 16MB'}), 400

                # Check file type (optional, remove if not needed)
                if not file.filename.lower().endswith(('.txt', '.csv', '.json')):
                    return jsonify({'error': f'File {file.filename} is not a supported file type'}), 400

                try:
                    text = file.read().decode('utf-8')
                    texts[file.filename] = text  # Store full content
                except UnicodeDecodeError:
                    return jsonify({'error': f'File {file.filename} is not a valid text file'}), 400
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    return jsonify({'error': f'Error processing {file.filename}'}), 500
        
        return render_template('results.html', files=texts)
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

if __name__ == '__main__':
    app.run(debug=True)
