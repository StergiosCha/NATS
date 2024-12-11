from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

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
                    text = file.read().decode('utf-8')
                    texts[file.filename] = text[:1000]  # Limit preview to first 1000 chars
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue
                
        if not texts:
            return render_template('upload.html', error="No valid files were uploaded")
            
        return render_template('results.html', files=texts)
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run()
