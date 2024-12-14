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

        # Debug print
        print(f"Number of files received: {len(files)}")

        for file in files:
            if file and file.filename:
                try:
                    # Read entire file
                    text = file.read().decode('utf-8')
                    print(f"Processing file: {file.filename}, length: {len(text)}")
                    
                    doc = nlp(text[:5000])  # Process first 5000 characters
                    tokens = [token.text for token in doc 
                            if not token.is_punct and not token.is_space]
                    
                    if tokens:
                        documents.append(TaggedDocument(words=tokens, tags=[file.filename]))
                        filenames.append(file.filename)
                        print(f"Added document: {file.filename}, tokens: {len(tokens)}")
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue

        print(f"Total documents processed: {len(documents)}")

        if len(documents) < 2:
            return jsonify({'error': f'Need at least 2 documents. Only processed: {len(documents)}'}), 400
