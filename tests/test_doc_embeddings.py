# tests/test_embeddings.py
import pytest
from app.models.doc_embeddings import DocEmbeddingsAnalyzer
from app.models.word_embeddings import WordEmbeddingsAnalyzer
import spacy
import numpy as np

@pytest.fixture
def sample_texts():
    nlp = spacy.load('el_core_news_md')
    return {
        'doc1.txt': nlp('This is the first document about analysis.'),
        'doc2.txt': nlp('This is the second document about processing.'),
        'doc3.txt': nlp('This is a completely different text about learning.')
    }

class TestDocEmbeddings:
    def test_create_embeddings(self, sample_texts):
        analyzer = DocEmbeddingsAnalyzer(vector_size=100)
        embeddings = analyzer.create_embeddings(sample_texts)
        
        assert len(embeddings) == 3
        assert all(isinstance(v, np.ndarray) for v in embeddings.values())
        assert all(v.shape == (100,) for v in embeddings.values())

    def test_document_similarity(self, sample_texts):
        analyzer = DocEmbeddingsAnalyzer()
        analyzer.create_embeddings(sample_texts)
        
        sim = analyzer.get_document_similarity('doc1.txt', 'doc2.txt')
        assert isinstance(sim, float)
        assert -1 <= sim <= 1

class TestWordEmbeddings:
    def test_create_embeddings(self, sample_texts):
        analyzer = WordEmbeddingsAnalyzer(vector_size=100)
        embeddings = analyzer.create_embeddings(sample_texts)
        
        assert len(embeddings) > 0
        assert all(isinstance(v, np.ndarray) for v in embeddings.values())
        assert all(v.shape == (100,) for v in embeddings.values())

    def test_similar_words(self, sample_texts):
        analyzer = WordEmbeddingsAnalyzer()
        analyzer.create_embeddings(sample_texts)
        
        # Test with a word that should be in vocabulary
        similar_words = analyzer.get_most_similar_words('document', n=2)
        assert len(similar_words) == 2
        assert all(isinstance(sim, float) for _, sim in similar_words)
