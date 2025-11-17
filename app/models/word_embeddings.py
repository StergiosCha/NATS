# app/models/word_embeddings.py
from gensim.models import Word2Vec
import numpy as np
from typing import Dict, Any
import spacy
from app.models.dimension_reducer import DimensionReducer

class WordEmbeddingsAnalyzer:
    def __init__(self, vector_size=100, window=5, min_count=2, epochs=20):
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.epochs = epochs
        self.nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
        self.dimension_reducer = DimensionReducer()
        
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using Word2Vec and dimension reduction"""
        # Process text
        doc = self.nlp(text[:10000])  # Limit for memory
        
        # Prepare sentences for Word2Vec
        sentences = [[token.text for token in doc]]
        
        # Train Word2Vec model
        model = Word2Vec(sentences,
                        vector_size=self.vector_size,
                        window=self.window,
                        min_count=self.min_count,
                        workers=4,
                        epochs=self.epochs)
        
        # Get word embeddings (most frequent words)
        word_vectors = {word: model.wv[word] 
                       for word in model.wv.index_to_key[:100]}  # Limit to top 100 words
        
        # Reduce dimensions and create visualizations
        visualizations = self.dimension_reducer.analyze_both(word_vectors)
        
        return {
            'pca_plot': visualizations['pca']['plot'],
            'tsne_plot': visualizations['tsne']['plot'],
            'embeddings': {word: vec.tolist() 
                          for word, vec in word_vectors.items()}
        }
