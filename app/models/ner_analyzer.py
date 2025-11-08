import spacy
from pyvis.network import Network
from collections import Counter, defaultdict
from typing import Dict, Any, List, Tuple
import os
import re
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots


from difflib import SequenceMatcher

def calculate_similarity(str1, str2):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def normalize_entities(entities, similarity_threshold=0.85):
    """
    Normalize similar entity names to a canonical form.
    Handles Greek declensions like Γιώργος/Γιώργου/Γιώργο
    """
    if not entities:
        return entities, {}
    
    normalized = {}
    entity_map = {}  # Maps original -> normalized
    canonical_forms = {}  # Tracks the canonical form for each cluster
    
    entity_list = list(entities.items())
    
    for entity, entity_type in entity_list:
        # Clean entity text
        entity_clean = entity.strip()
        if not entity_clean:
            continue
            
        # Try to find a similar existing entity
        found_match = False
        
        for canonical, norm_type in normalized.items():
            # Only compare entities of the same type
            if norm_type != entity_type:
                continue
            
            # Calculate similarity
            similarity = calculate_similarity(entity_clean, canonical)
            
            # If highly similar, map to canonical form
            if similarity >= similarity_threshold:
                entity_map[entity_clean] = canonical
                found_match = True
                break
        
        if not found_match:
            # This becomes a new canonical form
            normalized[entity_clean] = entity_type
            entity_map[entity_clean] = entity_clean
            canonical_forms[entity_clean] = entity_clean
    
    return normalized, entity_map


class EnhancedNERAnalyzer:
    def __init__(self):
        """Initialize enhanced NER with better Greek language support"""
        try:
            self.nlp = spacy.load('el_core_news_md')
        except OSError:
            print("Greek model not available, using English model")
            self.nlp = spacy.load('en_core_web_sm')
        
        # Clean, modern color palette
        self.entity_colors = {
            'PERSON': '#FF6B6B',
            'ORG': '#4ECDC4',
            'LOC': '#45B7D1',
            'GPE': '#96CEB4',
            'DATE': '#FFEAA7',
            'EVENT': '#EC7063',
            'PRODUCT': '#FADBD8',
            'MISC': '#FCF3CF'
        }
    
    def extract_entities(self, text: str, max_chars: int = None) -> Dict[str, str]:
        """Extract entities with quality filtering and normalization"""
        if max_chars is not None and len(text) > max_chars:
            print(f"⚠️ Text truncated from {len(text):,} to {max_chars:,} characters")
            doc = self.nlp(text[:max_chars])
        else:
            print(f"Processing full text: {len(text):,} characters")
            doc = self.nlp(text)
        
        entities = {}
        # Greek stopwords to filter out
        stopwords = {'και', 'για', 'με', 'σε', 'από', 'στο', 'στη', 'στον', 'στην', 
                    'δεν', 'θα', 'είναι', 'έχει', 'ήταν'}
        
        for ent in doc.ents:
            # Quality filters
            if (ent.label_ in self.entity_colors and 
                len(ent.text.strip()) > 1 and
                ent.text.lower() not in stopwords and
                not ent.text.isnumeric()):
                entities[ent.text] = ent.label_
        
        # Normalize similar entities (handles Greek declensions)
        normalized_entities, entity_map = normalize_entities(entities, similarity_threshold=0.85)
        
        print(f"Entity normalization: {len(entities)} → {len(normalized_entities)} unique entities")
        
        return normalized_entities
    
    def calculate_entity_importance(self, entities: Dict[str, str]) -> Dict[str, float]:
        """Calculate importance scores based on frequency"""
        entity_counts = Counter(entities.keys())
        total = sum(entity_counts.values())
        
        importance = {}
        for entity in entities.keys():
            importance[entity] = entity_counts[entity] / total
        
        return importance
    
    def find_relationships(self, doc, entities: Dict[str, str]) -> List[Tuple[str, str]]:
        """Find entity co-occurrences in sentences"""
        relationships = []
        added = set()
        
        for sent in doc.sents:
            sent_entities = [ent.text for ent in sent.ents if ent.text in entities]
            
            # Create edges between entities in the same sentence
            for i, ent1 in enumerate(sent_entities):
                for ent2 in sent_entities[i+1:]:
                    edge = tuple(sorted([ent1, ent2]))
                    if edge not in added:
                        relationships.append(edge)
                        added.add(edge)
        
        return relationships
    
    def create_network_visualization(self, text: str, output_dir: str = '.') -> Dict[str, Any]:
        """Create clean network visualization"""
        doc = self.nlp(text)
        
        # Get raw entities first
        raw_entities = {}
        stopwords = {'και', 'για', 'με', 'σε', 'από', 'στο', 'στη', 'στον', 'στην', 
                    'δεν', 'θα', 'είναι', 'έχει', 'ήταν'}
        
        for ent in doc.ents:
            if (ent.label_ in self.entity_colors and 
                len(ent.text.strip()) > 1 and
                ent.text.lower() not in stopwords and
                not ent.text.isnumeric()):
                raw_entities[ent.text] = ent.label_
        
        # Normalize entities
        entities, entity_map = normalize_entities(raw_entities, similarity_threshold=0.85)
        
        if not entities:
            return {'error': 'No entities found in text'}
        
        print(f"✓ Normalized {len(raw_entities)} entities to {len(entities)} unique entities")
        
        importance = self.calculate_entity_importance(entities)
        
        # Update relationships to use normalized names
        relationships = []
        added = set()
        
        for sent in doc.sents:
            sent_entities = [ent.text for ent in sent.ents if ent.text in raw_entities]
            # Map to normalized names
            sent_entities_normalized = [entity_map.get(e, e) for e in sent_entities]
            
            for i, ent1 in enumerate(sent_entities_normalized):
                for ent2 in sent_entities_normalized[i+1:]:
                    edge = tuple(sorted([ent1, ent2]))
                    if edge not in added and ent1 in entities and ent2 in entities:
                        relationships.append(edge)
                        added.add(edge)
        
        # Create network
        net = Network(
            height='700px', 
            width='100%', 
            bgcolor='#1a1a2e',
            font_color='white',
            notebook=False
        )
        
        # Add nodes
        for entity, label in entities.items():
            size = max(15, min(45, int(importance[entity] * 300)))
            
            net.add_node(
                entity,
                label=entity,
                color=self.entity_colors.get(label, '#ffffff'),
                size=size,
                title=f"{entity}<br>Type: {label}<br>Importance: {importance[entity]:.1%}",
                font={'size': 12, 'color': 'white'}
            )
        
        # Add edges
        for ent1, ent2 in relationships:
            net.add_edge(ent1, ent2, color='rgba(255,255,255,0.3)', width=1)
        
        # Better physics settings
        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "stabilization": {"iterations": 200},
                "barnesHut": {
                    "gravitationalConstant": -3000,
                    "centralGravity": 0.3,
                    "springLength": 150,
                    "springConstant": 0.05,
                    "damping": 0.15,
                    "avoidOverlap": 0.2
                }
            },
            "interaction": {
                "hover": true,
                "tooltipDelay": 100,
                "zoomView": true,
                "dragView": true
            }
        }
        """)
        
        # Save network
        os.makedirs(output_dir, exist_ok=True)
        timestamp = len([f for f in os.listdir(output_dir) if f.startswith('network_')])
        network_path = os.path.join(output_dir, f'network_{timestamp}.html')
        net.save_graph(network_path)
        
        # Create analytics visualizations
        viz_data = self.create_analytics_dashboard(entities, importance)
        
        return {
            'network_path': os.path.basename(network_path),
            'entities': entities,
            'entity_count': len(entities),
            'relationship_count': len(relationships),
            'importance_scores': importance,
            'visualizations': viz_data
        }
    
    def create_analytics_dashboard(self, entities: Dict[str, str], 
                                   importance: Dict[str, float]) -> Dict[str, Any]:
        """Create clean analytics charts"""
        
        # Count by type
        type_counts = Counter(entities.values())
        
        # Top entities
        top_entities = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:15]
        
        # Create figure with subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Entity Type Distribution', 'Top 15 Most Important Entities'),
            specs=[[{"type": "pie"}, {"type": "bar"}]],
            horizontal_spacing=0.15
        )
        
        # Pie chart
        fig.add_trace(
            go.Pie(
                labels=list(type_counts.keys()),
                values=list(type_counts.values()),
                marker=dict(colors=[self.entity_colors.get(t, '#999') for t in type_counts.keys()]),
                textinfo='label+percent',
                textfont=dict(size=12),
                hole=0.3
            ),
            row=1, col=1
        )
        
        # Bar chart
        fig.add_trace(
            go.Bar(
                x=[e[1]*100 for e in top_entities],
                y=[e[0] for e in top_entities],
                orientation='h',
                marker=dict(
                    color=[self.entity_colors.get(entities[e[0]], '#999') for e in top_entities],
                    line=dict(color='white', width=1)
                ),
                text=[f'{e[1]:.1%}' for e in top_entities],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Importance: %{x:.1f}%<extra></extra>'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=500,
            showlegend=False,
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            font=dict(family='Arial', size=12, color='#2c3e50'),
            margin=dict(l=20, r=20, t=60, b=20),
            title={
                'text': 'Named Entity Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#2c3e50'}
            }
        )
        
        fig.update_xaxes(title_text='Importance Score (%)', row=1, col=2)
        fig.update_yaxes(title_text='', row=1, col=2)
        
        return {
            'analytics_plot': json.loads(fig.to_json()),
            'stats': {
                'total_entities': len(entities),
                'unique_types': len(type_counts),
                'most_common_type': type_counts.most_common(1)[0][0] if type_counts else None
            }
        }
    
    def process_text(self, text: str, output_dir: str = '.') -> Dict[str, Any]:
        """Main entry point for processing"""
        return self.create_network_visualization(text, output_dir)