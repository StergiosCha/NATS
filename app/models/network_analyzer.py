# app/models/network_analyzer.py
import spacy
from pyvis.network import Network
import pandas as pd
from typing import Dict, List, Any
import os

class NetworkAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("el_core_news_md")
        # Disable unused components to save memory
        self.nlp.select_pipes(enable=['ner'])
        
        self.entity_colors = {
            'BAND': '#ff4444',      # Red for bands
            'LOC': '#44ff44',       # Green for locations
            'GPE': '#44ff44',       # Green for geo-political entities
            'ORG': '#4444ff',       # Blue for organizations
            'PERSON': '#ffff44',    # Yellow for people
            'DATE': '#ff44ff'       # Purple for dates
        }
        
    def create_network(self, text: str, output_dir: str = '.') -> Dict[str, Any]:
        """Create and visualize network of entities"""
        # Process only first 5000 characters to save memory
        doc = self.nlp(text[:5000])
        
        # Create interactive network
        net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')
        
        # Track entities and connections
        connections = []
        entities = {}
        
        # Process each sentence
        for sent in doc.sents:
            sentence_entities = []
            
            # Find named entities
            for ent in sent.ents:
                if ent.label_ in self.entity_colors:
                    sentence_entities.append((ent.label_, ent.text))
                    entities[ent.text] = ent.label_
            
            # Create connections
            self._process_connections(sentence_entities, sent.text, connections)
        
        # Build network
        self._build_network(net, entities, connections)
        
        # Save network
        network_path = os.path.join(output_dir, f'network_{len(os.listdir(output_dir))}.html')
        net.save_graph(network_path)
        
        return {
            'network_path': network_path,
            'entities': entities,
            'connections': connections
        }
    
    def _process_connections(self, sentence_entities, context, connections):
        for i, (type1, ent1) in enumerate(sentence_entities):
            for type2, ent2 in sentence_entities[i+1:]:
                connections.append((ent1, ent2, type1, type2, context))
    
    def _build_network(self, net, entities, connections):
        # Add nodes
        for entity, type_ in entities.items():
            net.add_node(entity, 
                        label=entity,
                        color=self.entity_colors.get(type_, '#ffffff'),
                        title=f"Type: {type_}")
        
        # Add edges
        for ent1, ent2, type1, type2, context in connections:
            net.add_edge(ent1, ent2, title=context)
