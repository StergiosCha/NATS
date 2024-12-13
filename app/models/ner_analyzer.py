import spacy
from pyvis.network import Network
from collections import Counter
from typing import Dict, Any
import os

class NERAnalyzer:
    def __init__(self):
        self.nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
        self.nlp.add_pipe('sentencizer')
        
        self.entity_colors = {
            'PERSON': '#ffff44',  # Yellow
            'ORG': '#4444ff',     # Blue
            'LOC': '#44ff44',     # Green
            'GPE': '#44ff44',     # Green
            'DATE': '#ff44ff'     # Purple
        }
    
    def process_text(self, text: str, output_dir: str) -> Dict[str, Any]:
        """Process text and create entity network"""
        # Process text in smaller chunk
        doc = self.nlp(text[:10000])
        
        # Track entities
        entities = {}
        entity_counts = Counter()
        connections = set()
        
        # Process entities
        for ent in doc.ents:
            if ent.label_ in self.entity_colors:
                entities[ent.text] = ent.label_
                entity_counts[ent.label_] += 1
        
        # Create network
        net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
        
        # Add nodes
        for entity, label in entities.items():
            net.add_node(entity, 
                        label=entity,
                        color=self.entity_colors.get(label, '#ffffff'),
                        title=f"Type: {label}")
        
        # Find connections in sentences
        for sent in doc.sents:
            sent_ents = [ent for ent in sent.ents if ent.label_ in self.entity_colors]
            for i, ent1 in enumerate(sent_ents):
                for ent2 in sent_ents[i+1:]:
                    connections.add((ent1.text, ent2.text))
                    net.add_edge(ent1.text, ent2.text, title=sent.text[:100])
        
        # Save network
        os.makedirs(output_dir, exist_ok=True)
        network_path = os.path.join(output_dir, f'network_{len(os.listdir(output_dir))}.html')
        net.save_graph(network_path)
        
        return {
            'entities': entities,
            'entity_counts': dict(entity_counts),
            'network_path': os.path.basename(network_path)
        }
