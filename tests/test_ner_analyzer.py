cat > tests/test_ner_analyzer.py << 'EOL'
import pytest
from app.models.ner_analyzer import NERAnalyzer
import spacy

@pytest.fixture
def sample_texts():
    nlp = spacy.load('el_core_news_md')
    return {
        'doc1.txt': nlp('John Smith works at Apple in New York.'),
        'doc2.txt': nlp('Microsoft was founded by Bill Gates in 1975.')
    }

def test_analyze_texts(sample_texts):
    analyzer = NERAnalyzer()
    results = analyzer.analyze_texts(sample_texts)
    
    assert len(results) == 2
    assert any(entity['text'] == 'John Smith' for entity in results['doc1.txt'])
    assert any(entity['text'] == 'Bill Gates' for entity in results['doc2.txt'])

def test_entity_counts(sample_texts):
    analyzer = NERAnalyzer()
    analyzer.analyze_texts(sample_texts)
    
    counts = analyzer.get_entity_counts()
    assert len(counts) == 2
    assert all(isinstance(v, dict) for v in counts.values())

def test_visualization(sample_texts):
    analyzer = NERAnalyzer()
    analyzer.analyze_texts(sample_texts)
    
    viz = analyzer.create_visualization()
    assert isinstance(viz, str)
    assert viz.startswith('{')  # Should be JSON string
EOL

git add tests/test_ner_analyzer.py
git commit -m "test: add ner analyzer tests"
