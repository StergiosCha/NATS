# wsgi.py
from flask import Flask, render_template, request, jsonify
import os
import spacy
from pyvis.network import Network
from collections import Counter
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px

app = Flask(__name__, template_folder='app/templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

# Initialize spacy with error handling
try:
    nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
    nlp.add_pipe('sentencizer')
except Exception as e:
    print(f"Error loading spacy model: {str(e)}")

# Create networks directory if it doesn't exist
networks_dir = os.path.join(app.static_folder, 'networks')
os.makedirs(networks_dir, exist_ok=True)

[rest of your code stays exactly the same until the last if block]

if __name__ == '__main__':
    # Get port from environment variable for Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
