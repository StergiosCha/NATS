# app/models/doc_embeddings.py
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px
import spacy
from typing import Dict, Any

class DocEmbeddingAnalyzer:
    def __init__(self):
        self.nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
        self.vector_size = 50  # Keep dimensions small
        
    def analyze_doc(self, text: str, reduction_type: str = 'pca') -> Dict[str, Any]:
        # Process first part of text
        doc = self.nlp(text[:5000])
        
        # Prepare document for Doc2Vec
        document = TaggedDocument(words=[token.text for token in doc], tags=['doc'])
        
        # Train Doc2Vec (minimal parameters)
        model = Doc2Vec([document], vector_size=self.vector_size, min_count=1, epochs=20)
        
        # Get document vector
        doc_vector = model.dv['doc']
        
        # Create visualization
        if reduction_type == 'pca':
            reducer = PCA(n_components=2)
        else:
            reducer = TSNE(n_components=2, perplexity=5)
            
        # Add plot
        fig = px.scatter(x=[doc_vector[0]], y=[doc_vector[1]])
        
        return {
            'embedding': doc_vector.tolist(),
            'plot': fig.to_json()
        }
