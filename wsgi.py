@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        analysis_type = request.form.get('analysis_type', 'NER')
        texts = {}

        if analysis_type == 'NER':
            # Process NER
            for file in files:
                if file and file.filename:
                    try:
                        text = file.read().decode('utf-8')
                        entities, entity_counts = process_text_safely(text)
                        texts[file.filename] = {
                            'preview': text[:200],
                            'entities': entities,
                            'entity_counts': entity_counts
                        }
                    except Exception as e:
                        print(f"Error processing {file.filename}: {str(e)}")
            
            return render_template('results.html',
                                files=texts,
                                analysis_type='NER')
        else:
            # Process Doc2Vec
            reduction_type = request.form.get('reduction_type', 'pca')
            documents = []
            filenames = []
            
            for file in files:
                if file and file.filename:
                    try:
                        text = file.read().decode('utf-8')
                        doc = nlp(text[:3000])
                        documents.append(TaggedDocument(words=[token.text for token in doc], 
                                                     tags=[file.filename]))
                        filenames.append(file.filename)
                    except Exception as e:
                        print(f"Error processing {file.filename}: {str(e)}")

            # Train Doc2Vec
            model = Doc2Vec(documents, vector_size=20, min_count=1, epochs=10)
            vectors = [model.dv[fname] for fname in filenames]

            # Dimension reduction
            if reduction_type == 'pca':
                reducer = PCA(n_components=2)
            else:
                reducer = TSNE(n_components=2, perplexity=min(30, len(vectors)-1))
            coords = reducer.fit_transform(vectors)

            # Create plot
            fig = px.scatter(x=coords[:, 0], y=coords[:, 1],
                           text=filenames,
                           title=f"Document Embeddings ({reduction_type.upper()})")

            texts['all_docs'] = {
                'plot': fig.to_json(),
                'reduction_type': reduction_type
            }

            return render_template('results.html',
                                files=texts,
                                analysis_type='Doc2Vec')

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500
