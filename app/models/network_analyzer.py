# Open app/models/network_analyzer.py and add this content:
cat > app/models/network_analyzer.py << 'EOL'
import spacy
import networkx as nx
from pyvis.network import Network
import pandas as pd
from typing import Dict, List, Set, Any
import os

class NetworkAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("el_core_news_md")
        self.entity_colors = {
            'BAND': '#ff4444',      # Red for bands
            'LOC': '#44ff44',       # Green for locations
            'GPE': '#44ff44',       # Green for geo-political entities
            'ORG': '#4444ff',       # Blue for organizations
            'PERSON': '#ffff44',    # Yellow for people
            'DATE': '#ff44ff'       # Purple for dates
        }
        self.known_bands = {
            'rotting christ', 'necromantia', 'varathron', 'septicflesh', 
            'thou art lord', 'astarte', 'zemial', 'kawir', 'naer mataron',
            'mortify', 'nightfall', 'horror of sadist', 'dark nova'
        }
        
    def create_network(self, text: str, output_dir: str = '.') -> Dict[str, Any]:
        """Create and visualize network of entities"""
        doc = self.nlp(text)
        
        # Create interactive network
        net = Network(notebook=True, height='750px', width='100%', 
                     bgcolor='#222222', font_color='white')
        
        # Track entities and connections
        connections = []
        entities = {}
        
        # Process each sentence
        for sent in doc.sents:
            sentence_entities = []
            
            # Find bands in sentence
            for band in self.known_bands:
                if band.lower() in sent.text.lower():
                    sentence_entities.append(('BAND', band.title()))
            
            # Find named entities
            for ent in sent.ents:
                if ent.label_ in ['LOC', 'GPE', 'ORG', 'PERSON', 'DATE']:
                    if ent.text.lower() not in self.known_bands:
                        sentence_entities.append((ent.label_, ent.text))
            
            # Create connections
            self._process_connections(sentence_entities, sent.text, connections, entities)
        
        # Build network
        self._build_network(net, entities, connections)
        
        # Generate output files
        result = self._generate_output(output_dir, connections, entities, net)
        
        return result
    
    def _process_connections(self, 
                           sentence_entities: List[tuple], 
                           context: str,
                           connections: List[tuple],
                           entities: Dict[str, str]) -> None:
        """Process connections between entities in a sentence"""
        for i, (type1, ent1) in enumerate(sentence_entities):
            for type2, ent2 in sentence_entities[i+1:]:
                connections.append((ent1, ent2, type1, type2, context))
                entities[ent1] = type1
                entities[ent2] = type2
    
    def _build_network(self,
                      net: Network,
                      entities: Dict[str, str],
                      connections: List[tuple]) -> None:
        """Build network with nodes and edges"""
        # Add nodes
        for entity, type_ in entities.items():
            net.add_node(entity, 
                        label=entity,
                        color=self.entity_colors.get(type_, '#ffffff'),
                        title=f"Type: {type_}")
        
        # Add edges
        for ent1, ent2, type1, type2, context in connections:
            net.add_edge(ent1, ent2, title=context)
    
    def _generate_output(self,
                        output_dir: str,
                        connections: List[tuple],
                        entities: Dict[str, str],
                        net: Network) -> Dict[str, Any]:
        """Generate output files and summaries"""
        # Create output paths
        base_path = os.path.join(output_dir, 'network_analysis')
        network_path = f"{base_path}_network.html"
        csv_path = f"{base_path}_connections.csv"
        
        # Save network visualization
        net.write_html(network_path)
        
        # Create and save connections summary
        summary = pd.DataFrame(connections, 
                             columns=['Entity 1', 'Entity 2', 
                                    'Type 1', 'Type 2', 'Context'])
        summary.to_csv(csv_path, index=False, encoding='utf-8')
        
        # Prepare entity summary
        entity_summary = {}
        for entity_type in set(entities.values()):
            type_entities = [e for e, t in entities.items() if t == entity_type]
            if type_entities:
                entity_summary[entity_type] = type_entities
        
        return {
            'network': net,
            'connections': summary,
            'entities': entity_summary,
            'network_path': network_path,
            'csv_path': csv_path
        }

