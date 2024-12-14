@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        analysis_type = request.form.get('analysis_type', 'NER')
        reduction_type = request.form.get('reduction_type', 'pca')

        documents = []
        filenames = []

        for file in files:
            if file and file.filename:
                try:
                    # Try different encodings
                    content = file.read()
                    try:
                        text = content.decode('utf-8-sig')  # Try UTF-8 with BOM first
                    except UnicodeDecodeError:
                        try:
                            text = content.decode('cp1253')  # Try Greek Windows encoding
                        except UnicodeDecodeError:
                            text = content.decode('iso-8859-7')  # Try Greek ISO encoding
                    
                    doc = nlp(text[:5000])
                    tokens = [token.text for token in doc 
                            if not token.is_punct and not token.is_space]
                    
                    if tokens:
                        documents.append(TaggedDocument(words=tokens, tags=[file.filename]))
                        filenames.append(file.filename)
                        print(f"Successfully processed: {file.filename}")
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue
