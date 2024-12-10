# tests/test_network_analyzer.py
import pytest
from app.models.network_analyzer import NetworkAnalyzer
import os
import pandas as pd

@pytest.fixture
def sample_text():
    return """
    Rotting Christ performed in Athens with Necromantia in 1996.
    The concert was organized by Varathron at Olympic Stadium.
    Later, Septicflesh collaborated with Kawir in Thessaloniki.
    """

@pytest.fixture
def analyzer():
    return NetworkAnalyzer()

def test_network_creation(analyzer, sample_text, tmp_path):
    # Analyze text
    result = analyzer.create_network(sample_text, output_dir=str(tmp_path))
    
    # Check if output files were created
    assert os.path.exists(result['network_path'])
    assert os.path.exists(result['csv_path'])
    
    # Check if connections DataFrame has correct structure
    connections_df = result['connections']
    assert isinstance(connections_df, pd.DataFrame)
    assert all(col in connections_df.columns 
              for col in ['Entity 1', 'Entity 2', 'Type 1', 'Type 2', 'Context'])
    
    # Check if entities were found
    entities = result['entities']
    assert len(entities) > 0
    assert 'BAND' in entities  # Should find band entities
    assert 'LOC' in entities or 'GPE' in entities  # Should find location entities

def test_entity_detection(analyzer, sample_text):
    result = analyzer.create_network(sample_text)
    
    # Check if known bands were detected
    bands = result['entities'].get('BAND', [])
    assert 'Rotting Christ' in bands
    assert 'Necromantia' in bands
    assert 'Varathron' in bands
    
    # Check if locations were detected
    locations = result['entities'].get('LOC', []) + result['entities'].get('GPE', [])
    assert 'Athens' in locations
    assert 'Thessaloniki' in locations

def test_empty_text(analyzer):
    result = analyzer.create_network("")
    assert len(result['connections']) == 0
    assert len(result['entities']) == 0

def test_no_entities_text(analyzer):
    result = analyzer.create_network("This text contains no named entities.")
    assert len(result['connections']) == 0
    assert len(result['entities']) == 0
