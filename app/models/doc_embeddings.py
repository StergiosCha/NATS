# app/models/doc_embeddings.py
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
from typing import Dict, List, Any
import spacy
from .dimension_reducer import DimensionReducer

class DocEmbeddingsAnalyzer:
    def __init__(self, vector_size=150, window=12, min_count=2, epochs=35):
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.epochs = epochs
        self.model = None
        self.embeddings = {}
        
    def create_embeddings(self, texts: Dict[str, spacy.tokens.Doc]) -> Dict[str, np.ndarray]:
        """Create document embeddings from preprocessed texts"""
        # Prepare documents for Doc2Vec
        documents = [
            TaggedDocument(
                words=[token.text for token in doc if not token.is_punct],
                tags=[filename]
            )
            for filename, doc in texts.items()
        ]
        
        # Train Doc2Vec model
        self.model = Doc2Vec(
            documents,
            vector_size=self.vector_size,
            window=self.window,
            min_count=self.min_count,
            workers=4,
            epochs=self.epochs
        )
        
        # Generate embeddings
        self.embeddings = {
            filename: self.model.dv[filename]
            for filename in texts.keys()
        }
        
        return self.embeddings
    
    def get_document_similarity(self, doc1: str, doc2: str) -> float:
        """Calculate cosine similarity between two documents"""
        if doc1 not in self.embeddings or doc2 not in self.embeddings:
            raise KeyError("Document not found in embeddings")
            
        vec1 = self.embeddings[doc1]
        vec2 = self.embeddings[doc2]
        
        similarity = np.dot(vec1, vec2) / (
            np.linalg.norm(vec1) * np.linalg.norm(vec2)
        )
        
        return float(similarity)
    
    def visualize_embeddings(self, method: str = 'both') -> Dict[str, Any]:
        """Visualize document embeddings using PCA and/or t-SNE"""
        if not self.embeddings:
            raise ValueError("No embeddings available. Run create_embeddings first.")
            
        reducer = DimensionReducer(n_components=2)
        
        if method.lower() == 'both':
            return reducer.analyze_both_methods(self.embeddings)
        else:
            return reducer.reduce_embeddings(self.embeddings, method)
