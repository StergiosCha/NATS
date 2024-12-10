cat > tests/test_word_embeddings.py << 'EOL'
import pytest
from app.models.word_embeddings import WordEmbeddingsAnalyzer
import spacy
import numpy as np

@pytest.fixture
def sample_texts():
    nlp = spacy.load('el_core_news_md')
    return {
        'doc1.txt': nlp('This is a sample document about artificial intelligence.'),
        'doc2.txt': nlp('Machine learning and deep learning are part of AI.'),
        'doc3.txt': nlp('Neural networks process data using layers of neurons.')
    }

def test_create_embeddings(sample_texts):
    analyzer = WordEmbeddingsAnalyzer(vector_size=100)
    embeddings = analyzer.create_embeddings(sample_texts)
    
    assert len(embeddings) > 0
    assert all(isinstance(v, np.ndarray) for v in embeddings.values())
    assert all(v.shape == (100,) for v in embeddings.values())

def test_similar_words(sample_texts):
    analyzer = WordEmbeddingsAnalyzer(vector_size=100)
    analyzer.create_embeddings(sample_texts)
    
    # Test with a word that should be in vocabulary
    similar = analyzer.get_most_similar_words('learning', n=2)
    assert len(similar) == 2
    assert all(isinstance(sim, float) for _, sim in similar)

def test_get_word_vector(sample_texts):
    analyzer = WordEmbeddingsAnalyzer(vector_size=100)
    analyzer.create_embeddings(sample_texts)
    
    vector = analyzer.get_word_vector('neural')
    assert isinstance(vector, np.ndarray)
    assert vector.shape == (100,)

def test_missing_word_error():
    analyzer = WordEmbeddingsAnalyzer()
    
    with pytest.raises(ValueError):
        analyzer.get_most_similar_words('test')
        
    with pytest.raises(ValueError):
        analyzer.get_word_vector('test')
EOL

git add tests/test_word_embeddings.py
git commit -m "test: add word embeddings tests"
git push origin main
