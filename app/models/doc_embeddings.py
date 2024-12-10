# app/models/doc_embeddings.py
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
from typing import Dict, List, Any
import spacy

class DocEmbeddingsAnalyzer:
    def __init__(self, vector_size=150, window=12, min_count=2, epochs=35):
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.epochs = epochs
        self.model = None
        self.embeddings = {}
        
    def create_embeddings(self, texts: Dict[str, spacy.tokens.Doc]) -> Dict[str, np.ndarray]:
        """
        Create document embeddings from preprocessed texts
        
        Args:
            texts: Dictionary of filename -> spaCy Doc
            
        Returns:
            Dictionary of filename -> embedding vector
        """
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
        
        # Generate and store embeddings
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
    
    def get_all_similarities(self) -> Dict[str, Dict[str, float]]:
        """Calculate similarities between all document pairs"""
        similarities = {}
        documents = list(self.embeddings.keys())
        
        for i, doc1 in enumerate(documents):
            similarities[doc1] = {}
            for doc2 in documents[i+1:]:
                similarity = self.get_document_similarity(doc1, doc2)
                similarities[doc1][doc2] = similarity
        
        return similarities
    
    def find_most_similar(self, document: str, n: int = 3) -> List[tuple]:
        """Find n most similar documents to the given document"""
        if document not in self.embeddings:
            raise KeyError(f"Document '{document}' not found in embeddings")
            
        similarities = []
        for other_doc in self.embeddings.keys():
            if other_doc != document:
                sim = self.get_document_similarity(document, other_doc)
                similarities.append((other_doc, sim))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:n]
