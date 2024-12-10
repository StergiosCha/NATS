# tests/test_doc_embeddings.py
import pytest
from app.models.doc_embeddings import DocEmbeddingsAnalyzer
import spacy
import numpy as np

@pytest.fixture
def sample_texts():
    nlp = spacy.load('el_core_news_md')
    return {
        'doc1.txt': nlp('This is the first document.'),
        'doc2.txt': nlp('This is the second document.'),
        'doc3.txt': nlp('This is a completely different text.')
    }

def test_create_embeddings(sample_texts):
    analyzer = DocEmbeddingsAnalyzer(vector_size=100)
    embeddings = analyzer.create_embeddings(sample_texts)
    
    assert len(embeddings) == 3
    assert all(isinstance(v, np.ndarray) for v in embeddings.values())
    assert all(v.shape == (100,) for v in embeddings.values())

def test_document_similarity(sample_texts):
    analyzer = DocEmbeddingsAnalyzer()
    analyzer.create_embeddings(sample_texts)
    
    sim = analyzer.get_document_similarity('doc1.txt', 'doc2.txt')
    assert isinstance(sim, float)
    assert -1 <= sim <= 1
