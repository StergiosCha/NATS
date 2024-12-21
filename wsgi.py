from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        
        # Just test file upload
        texts = {}
        for file in files:
            if file and file.filename:
                text = file.read().decode('utf-8')[:1000]  # Just first 1000 chars
                texts[file.filename] = {'preview': text}
        
        return render_template('results.html', files=texts)
        
    except Exception as e:
        print(f"Upload error: {str(e)}")  # Debug print
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
