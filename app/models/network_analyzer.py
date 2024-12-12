# app/models/network_analyzer.py
import spacy
from pyvis.network import Network
from typing import Dict, Any
import os

class NetworkAnalyzer:
    def __init__(self):
        # Load small model instead
        self.nlp = spacy.load("el_core_news_md", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
        
        self.entity_colors = {
            'LOC': '#44ff44',
            'GPE': '#44ff44',
            'ORG': '#4444ff',
            'PERSON': '#ffff44',
            'DATE': '#ff44ff'
        }
        
    def create_network(self, text: str, output_dir: str = '.') -> Dict[str, Any]:
        # Process only first 3000 characters
        doc = self.nlp(text[:3000])
        
        net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
        entities = {}
        
        # Simplified entity processing
        for ent in doc.ents:
            if ent.label_ in self.entity_colors:
                entities[ent.text] = ent.label_
                net.add_node(ent.text, 
                            label=ent.text,
                            color=self.entity_colors[ent.label_],
                            title=f"Type: {ent.label_}")
        
        network_path = os.path.join(output_dir, f'network_{len(os.listdir(output_dir))}.html')
        net.save_graph(network_path)
        
        return {
            'network_path': network_path,
            'entities': entities
        }
