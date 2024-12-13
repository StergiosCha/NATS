# app/models/doc_embeddings.py
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
from typing import Dict, Any
import spacy
from app.models.dimension_reducer import DimensionReducer

class DocEmbeddingsAnalyzer:
    def __init__(self, vector_size=100, window=5, min_count=2, epochs=20):
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.epochs = epochs
        self.nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
        self.dimension_reducer = DimensionReducer()
        
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using Doc2Vec and dimension reduction"""
        # Process text
        doc = self.nlp(text[:10000])  # Limit for memory
        
        # Prepare document for Doc2Vec
        documents = [TaggedDocument(words=[token.text for token in doc], tags=['text'])]
        
        # Train Doc2Vec model
        model = Doc2Vec(documents,
                       vector_size=self.vector_size,
                       window=self.window,
                       min_count=self.min_count,
                       workers=4,
                       epochs=self.epochs)
        
        # Get document embedding
        embedding = {'text': model.dv['text']}
        
        # Reduce dimensions and create visualizations
        visualizations = self.dimension_reducer.analyze_both(embedding)
        
        return {
            'pca_plot': visualizations['pca']['plot'],
            'tsne_plot': visualizations['tsne']['plot'],
            'embedding': embedding['text'].tolist()
        }
