from flask import Flask, request, jsonify, render_template
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px
import spacy

# Initialize Flask app
app = Flask(__name__)

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

def process_text_safely(text):
    """Process text with NER and return entities and counts."""
    doc = nlp(text)
    entities = []
    entity_counts = {}
    
    for ent in doc.ents:
        entities.append({
            'text': ent.text,
            'label': ent.label_,
            'start': ent.start_char,
            'end': ent.end_char
        })
        entity_counts[ent.label_] = entity_counts.get(ent.label_, 0) + 1
    
    return entities, entity_counts

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

if __name__ == '__main__':
    app.run(debug=True)
