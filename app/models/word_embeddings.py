# app/models/word_embeddings.py
from gensim.models import Word2Vec
import numpy as np
from typing import Dict, List, Any
import spacy

class WordEmbeddingsAnalyzer:
    def __init__(self, vector_size=150, window=12, min_count=2, epochs=35):
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.epochs = epochs
        self.model = None
        self.embeddings = {}
        
    def create_embeddings(self, texts: Dict[str, spacy.tokens.Doc]) -> Dict[str, np.ndarray]:
        """Create word embeddings from preprocessed texts"""
        # Prepare sentences
        sentences = [
            [token.text for token in doc if not token.is_punct]
            for doc in texts.values()
        ]
        
        # Train Word2Vec model
        self.model = Word2Vec(
            sentences,
            vector_size=self.vector_size,
            window=self.window,
            min_count=self.min_count,
            workers=4,
            epochs=self.epochs
        )
        
        # Store word embeddings
        self.embeddings = {
            word: self.model.wv[word]
            for word in self.model.wv.index_to_key
        }
        
        return self.embeddings
        
    def get_most_similar_words(self, word: str, n: int = 10) -> List[tuple]:
        """Find n most similar words to the given word"""
        if not self.model:
            raise ValueError("Model not trained yet")
            
        try:
            return self.model.wv.most_similar(word, topn=n)
        except KeyError:
            raise KeyError(f"Word '{word}' not in vocabulary")
            
    def get_word_vector(self, word: str) -> np.ndarray:
        """Get vector for a specific word"""
        if not self.model:
            raise ValueError("Model not trained yet")
            
        try:
            return self.model.wv[word]
        except KeyError:
            raise KeyError(f"Word '{word}' not in vocabulary")