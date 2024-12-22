from flask import Flask, render_template, request, jsonify
import os
import spacy
from pyvis.network import Network
from collections import Counter
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px
import chardet  # For encoding detection

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max upload size

# Initialize spaCy with error handling
try:
    nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
    nlp.add_pipe('sentencizer')
except Exception as e:
    print(f"Error loading spaCy model: {str(e)}")

# Create networks directory if it doesn't exist
networks_dir = os.path.join(app.static_folder or 'static', 'networks')
os.makedirs(networks_dir, exist_ok=True)


def read_file_safely(file):
    """Read a file with proper encoding handling."""
    try:
        # Try reading with UTF-8 first
        text = file.read().decode('utf-8')
    except UnicodeDecodeError as e:
        print(f"UTF-8 decoding failed: {str(e)}")
        # Detect encoding and fallback
        file.seek(0)  # Reset pointer
        raw_data = file.read()
        detected_encoding = chardet.detect(raw_data)['encoding']
        print(f"Detected encoding: {detected_encoding}")
        text = raw_data.decode(detected_encoding, errors='ignore')  # Fallback decoding

    return text


def process_text_safely(text):
    """Process text with minimal memory usage."""
    entities = {}
    entity_counts = Counter()
    connections = set()

    # Only process first 10,000 characters for now
    doc = nlp(text[:10000])

    # Process entities
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
            entities[ent.text] = ent.label_
            entity_counts[ent.label_] += 1

    # Find connections
    for sent in doc.sents:
        sent_ents = [ent for ent in sent.ents if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']]
        for i, ent1 in enumerate(sent_ents):
            for ent2 in sent_ents[i + 1:]:
                connections.add((ent1.text, ent2.text))

    return entities, dict(entity_counts), connections


def process_doc2vec(files, reduction_type='pca'):
    """Process files with Doc2Vec and dimension reduction."""
    documents = []
    filenames = []

    for file in files:
        if file and file.filename:
            try:
                text = read_file_safely(file)
                print(f"Processing file: {file.filename}, Content length: {len(text)}")

                if len(text.strip()) == 0:
                    print(f"File {file.filename} is empty.")
                    continue

                doc = nlp(text[:3000])  # Process only first 3,000 characters
                tokens = [token.text for token in doc if not token.is_space]
                documents.append(TaggedDocument(words=tokens, tags=[file.filename]))
                filenames.append(file.filename)
                file.seek(0)
            except Exception as e:
                print(f"Error processing {file.filename}: {str(e)}")
                continue

    if not documents:
        print("No valid documents found.")
        return None, None

    model = Doc2Vec(documents, vector_size=20, min_count=1, epochs=10)
    vectors = [model.dv[fname] for fname in filenames]

    if reduction_type == 'pca':
        reducer = PCA(n_components=2)
    else:
        reducer = TSNE(n_components=2, perplexity=min(3, len(vectors) - 1))

    coords = reducer.fit_transform(vectors)
    fig = px.scatter(x=coords[:, 0], y=coords[:, 1],
                     text=filenames,
                     title=f"Document Embeddings ({reduction_type.upper()})")

    return fig.to_json(), filenames


@app.route('/')
def home():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        analysis_type = request.form.get('analysis_type', 'NER')
        reduction_type = request.form.get('reduction_type', 'pca')

        print(f"Uploaded files: {[file.filename for file in files]}")

        if analysis_type == 'NER':
            texts = {}
            os.makedirs('static/networks', exist_ok=True)

            for file in files:
                if file and file.filename:
                    try:
                        text = read_file_safely(file)

                        # Process text
                        entities, entity_counts, connections = process_text_safely(text)

                        # Create network visualization
                        net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
                        for entity, label in entities.items():
                            color_map = {
                                'PERSON': '#ffff44',
                                'ORG': '#4444ff',
                                'LOC': '#44ff44',
                                'GPE': '#44ff44',
                                'DATE': '#ff44ff'
                            }
                            net.add_node(entity, label=entity, color=color_map.get(label, '#ffffff'),
                                         title=f"Type: {label}")

                        for ent1, ent2 in connections:
                            net.add_edge(ent1, ent2)

                        network_filename = f'networks/network_{len(texts)}.html'
                        net.save_graph(f'static/{network_filename}')

                        texts[file.filename] = {
                            'preview': text[:200],
                            'entities': entities,
                            'network_path': network_filename,
                            'entity_counts': entity_counts,
                        }

                    except Exception as e:
                        print(f"Error processing {file.filename}: {str(e)}")
                        continue

            return render_template('results.html', files=texts, analysis_type='NER')

        elif analysis_type == 'Doc2Vec':
            plot_json, filenames = process_doc2vec(files, reduction_type)

            if plot_json is None:
                return jsonify({'error': 'No valid documents to process'}), 400

            results = {
                'all_docs': {
                    'plot': plot_json,
                    'filenames': filenames,
                }
            }

            return render_template('results.html', files=results, analysis_type='Doc2Vec')

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
