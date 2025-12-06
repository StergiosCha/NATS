import spacy
from pyvis.network import Network
import networkx as nx
from typing import Dict, Any, List, Tuple
import os
import json
import numpy as np
from collections import Counter, defaultdict
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    import community as community_louvain
    COMMUNITY_AVAILABLE = True
except ImportError:
    COMMUNITY_AVAILABLE = False


from difflib import SequenceMatcher
import unicodedata

def remove_greek_accents(text):
    """Remove Greek accent marks for better matching"""
    # Decompose characters and remove combining marks
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')

def normalize_greek_entity(text, entity_type):
    """Comprehensive Greek entity normalization using rules and lemmatization"""
    text = text.strip()
    
    # Apply Greek-specific rules based on entity type
    if entity_type == 'PERSON' and len(text) > 4:
        # Normalize person names to masculine nominative
        if text.endswith('άκη'):
            text = text[:-1] + 'ης'  # Νικολάκη -> Νικολάκης
        elif text.endswith('ίκη'):
            text = text[:-1] + 'ης'  # Γιωργίκη -> Γιωργίκης
        elif text.endswith('ου'):
            text = text[:-2] + 'ος'  # Γιώργου → Γιώργος
        elif text.endswith('ο') and not text.endswith('ιο'):
            text = text[:-1] + 'ος'  # Γιώργο → Γιώργος
        elif text.endswith('ε') and len(text) > 5:
            text = text[:-1] + 'ος'  # Γιώργε → Γιώργος
    
    elif entity_type in ['LOC', 'GPE'] and len(text) > 5:
        # Normalize place names
        if text.endswith('ης'):
            text = text[:-1]  # Φρανκφούρτης → Φρανκφούρτη
        elif text.endswith('ου'):
            text = text[:-2] + 'η'  # Αθήνου → Αθήνη
    
    return text

def find_similar_entity(new_entity, existing_entities, entity_type, threshold=0.80):
    """Find similar entity in existing list using fuzzy matching"""
    # Remove accents for better matching
    new_normalized = remove_greek_accents(new_entity.lower())
    
    for existing in existing_entities:
        if existing_entities[existing] != entity_type:
            continue  # Only compare same types
        
        existing_normalized = remove_greek_accents(existing.lower())
        
        # Calculate similarity without accents
        similarity = SequenceMatcher(None, new_normalized, existing_normalized).ratio()
        
        if similarity >= threshold:
            return existing
    
    return None


class EnhancedNetworkAnalyzer:
    def __init__(self):
        """Initialize enhanced network analyzer"""
        try:
            self.nlp = spacy.load("el_core_news_md", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler'])
        except:
            self.nlp = spacy.load("en_core_web_sm", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
        
        self.nlp.add_pipe('sentencizer')
        
        self.entity_colors = {
            'PERSON': '#FF6B6B',
            'ORG': '#4ECDC4',
            'LOC': '#45B7D1',
            'GPE': '#96CEB4',
            'MISC': '#FCF3CF'
        }
    
    def process_text_in_chunks(self, text: str, chunk_size: int = 50000):
        """Process long text in chunks to avoid memory/timeout issues"""
        if len(text) <= chunk_size:
            return self.nlp(text)
        
        print(f"Processing text in chunks: {len(text):,} chars, chunk size: {chunk_size:,}", flush=True)
        
        # Split text into manageable chunks at sentence boundaries
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # Get a chunk
            end_pos = min(current_pos + chunk_size, len(text))
            
            # If not at end, try to break at sentence boundary
            if end_pos < len(text):
                # Look for sentence endings in last 1000 chars of chunk
                chunk_text = text[current_pos:end_pos]
                last_period = max(
                    chunk_text.rfind('. '),
                    chunk_text.rfind('! '),
                    chunk_text.rfind('? '),
                    chunk_text.rfind('.\n')
                )
                
                if last_period > chunk_size - 1000:  # Found a good break point
                    end_pos = current_pos + last_period + 1
            
            chunks.append(text[current_pos:end_pos])
            current_pos = end_pos
        
        print(f"Split into {len(chunks)} chunks", flush=True)
        
        # Process each chunk and combine entities
        all_ents = []
        all_sents = []
        
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...", flush=True)
            chunk_doc = self.nlp(chunk)
            all_ents.extend(chunk_doc.ents)
            all_sents.extend(chunk_doc.sents)
        
        # Create a combined pseudo-doc
        class CombinedDoc:
            def __init__(self, ents, sents):
                self.ents = ents
                self.sents = sents
        
        return CombinedDoc(all_ents, all_sents)
    
    def extract_entities_and_relationships(self, text: str, max_chars: int = None) -> Tuple[Dict[str, str], List[Tuple[str, str, float]]]:
        """Extract entities and calculate relationship strengths"""
        print(f"Processing text: {len(text):,} characters", flush=True)
        
        # Use chunking for long texts
        if len(text) > 50000:
            doc = self.process_text_in_chunks(text, chunk_size=50000)
        else:
            doc = self.nlp(text)
        
        entities = {}
        entity_sentences = defaultdict(list)
        
        # Extract entities with filtering
        stopwords = {
            'και', 'για', 'με', 'σε', 'από', 'στο', 'στη', 'στον', 'στην', 'στους', 'στις',
            'δεν', 'θα', 'να', 'ο', 'η', 'το', 'οι', 'τα', 'των', 'του', 'της', 'τον', 'την',
            'ένα', 'μια', 'ένας', 'μία', 'είναι', 'ήταν', 'έχει', 'έχουν', 'πώς', 'πού', 'πο',
            'αυτό', 'αυτή', 'αυτός', 'που', 'πως', 'ως', 'σαν', 'όταν', 'αν', 'αλλά', 'μα'
        }
        for ent in doc.ents:
            if (ent.label_ in self.entity_colors and 
                len(ent.text.strip()) > 2 and  # Minimum 3 characters
                ent.text.lower() not in stopwords and
                not ent.text.lower() in ['πο', 'πω', 'πώς']):  # Extra Greek fragments
                entities[ent.text] = ent.label_
                entity_sentences[ent.text].append(ent.sent.text if hasattr(ent, 'sent') else "")
        
        print(f"Found {len(entities)} entities", flush=True)
        
        # Calculate relationship strengths - OPTIMIZED
        print("Calculating relationships...", flush=True)
        relationships = []
        entity_list = list(entities.keys())
        
        # Build index: which entities appear in which sentences
        sentence_to_entities = []
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            entities_in_sent = [e for e in entity_list if e.lower() in sent_text]
            if len(entities_in_sent) > 1:  # Only care about sentences with 2+ entities
                sentence_to_entities.append(entities_in_sent)
        
        print(f"Processing {len(sentence_to_entities)} sentences with multiple entities...", flush=True)
        
        # Count co-occurrences and store context sentences
        co_occurrence_counts = defaultdict(int)
        co_occurrence_contexts = defaultdict(list)
        
        for sent in doc.sents:
            sent_text = sent.text
            sent_lower = sent_text.lower()
            entities_in_sent = [e for e in entity_list if e.lower() in sent_lower]
            
            if len(entities_in_sent) > 1:
                # Create pairs from entities in this sentence
                for i, ent1 in enumerate(entities_in_sent):
                    for ent2 in entities_in_sent[i+1:]:
                        pair = tuple(sorted([ent1, ent2]))
                        co_occurrence_counts[pair] += 1
                        # Store the sentence context (limit to first 3 examples)
                        if len(co_occurrence_contexts[pair]) < 3:
                            co_occurrence_contexts[pair].append(sent_text[:200])  # First 200 chars
        
        # Convert to relationships list with context
        relationships = []
        for (e1, e2), count in co_occurrence_counts.items():
            relationships.append({
                'entities': (e1, e2),
                'strength': float(count),
                'contexts': co_occurrence_contexts[(e1, e2)]
            })
        
        print(f"Found {len(relationships)} relationships", flush=True)
        
        return entities, relationships
    
    def detect_communities(self, entities: Dict[str, str], relationships: List[Tuple[str, str, float]]) -> Dict[str, int]:
        """Detect communities using networkx"""
        if not relationships or not COMMUNITY_AVAILABLE:
            return {entity: 0 for entity in entities.keys()}
        
        G = nx.Graph()
        G.add_nodes_from(entities.keys())
        
        for rel in relationships:
            ent1, ent2 = rel['entities']
            weight = rel['strength']
            G.add_edge(ent1, ent2, weight=weight)
        
        try:
            communities = community_louvain.best_partition(G)
        except:
            communities = {entity: 0 for entity in entities.keys()}
        
        return communities
    
    def calculate_centrality(self, entities: Dict[str, str], relationships: List[Tuple[str, str, float]]) -> Dict[str, Dict[str, float]]:
        """Calculate centrality measures"""
        if not relationships:
            return {entity: {'degree': 0, 'betweenness': 0, 'pagerank': 0} 
                   for entity in entities.keys()}
        
        G = nx.Graph()
        G.add_nodes_from(entities.keys())
        
        for rel in relationships:
            ent1, ent2 = rel['entities']
            weight = rel['strength']
            G.add_edge(ent1, ent2, weight=weight)
        
        betweenness = nx.betweenness_centrality(G)
        pagerank = nx.pagerank(G)
        
        centrality_measures = {}
        for entity in entities.keys():
            centrality_measures[entity] = {
                'degree': G.degree(entity),
                'betweenness': betweenness.get(entity, 0),
                'pagerank': pagerank.get(entity, 0)
            }
        
        return centrality_measures
    
    def create_network_graph(self, text: str, output_dir: str = '.') -> Dict[str, Any]:
        """Create interactive network visualization"""
        
        entities, relationships = self.extract_entities_and_relationships(text)
        
        if not entities:
            return {'error': 'No entities found in text'}
        
        print("Detecting communities...", flush=True)
        communities = self.detect_communities(entities, relationships)
        
        print("Calculating centrality...", flush=True)
        centrality = self.calculate_centrality(entities, relationships)
        
        print("Creating network visualization...", flush=True)
        
        # Create network visualization
        net = Network(
            height='800px', 
            width='100%', 
            bgcolor='#0f1419',
            font_color='white',
            notebook=False
        )
        
        # Community colors
        community_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                           '#DDA0DD', '#98D8C8', '#F7DC6F']
        
        # Add nodes
        for entity, entity_type in entities.items():
            community_id = communities.get(entity, 0)
            color = community_colors[community_id % len(community_colors)]
            
            degree = centrality[entity]['degree']
            pagerank = centrality[entity]['pagerank']
            size = max(20, min(60, int(pagerank * 1000 + degree * 3)))
            
            net.add_node(
                entity,
                label=entity,
                color=color,
                size=size,
                title=f"<b>{entity}</b><br>Type: {entity_type}<br>Community: {community_id}<br>Connections: {degree}<br>PageRank: {pagerank:.4f}",
                font={'size': 14, 'color': 'white', 'face': 'arial'}
            )
        
        # Add edges with context
        for rel in relationships:
            ent1, ent2 = rel['entities']
            strength = rel['strength']
            contexts = rel['contexts']
            
            width = max(1, min(8, int(strength * 2)))
            
            # Build tooltip with context sentences
            tooltip = f"<b>{ent1} ↔ {ent2}</b><br>"
            tooltip += f"Co-occurrences: {int(strength)}<br><br>"
            tooltip += "<b>Example sentences:</b><br>"
            for i, ctx in enumerate(contexts[:3], 1):
                tooltip += f"{i}. {ctx}...<br>"
            
            net.add_edge(ent1, ent2, 
                        width=width, 
                        color='rgba(255,255,255,0.25)',
                        title=tooltip)
        
        # Physics configuration
        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "stabilization": {"iterations": 250},
                "barnesHut": {
                    "gravitationalConstant": -4000,
                    "centralGravity": 0.4,
                    "springLength": 120,
                    "springConstant": 0.05,
                    "damping": 0.15,
                    "avoidOverlap": 0.3
                }
            },
            "interaction": {
                "hover": true,
                "tooltipDelay": 50,
                "navigationButtons": true,
                "keyboard": true
            },
            "nodes": {
                "borderWidth": 2,
                "borderWidthSelected": 4,
                "font": {
                    "size": 14,
                    "face": "arial"
                }
            }
        }
        """)
        
        # Save network
        os.makedirs(output_dir, exist_ok=True)
        timestamp = len([f for f in os.listdir(output_dir) if f.startswith('network_')])
        network_path = os.path.join(output_dir, f'network_{timestamp}.html')
        net.save_graph(network_path)
        
        print(f"Network saved to {network_path}", flush=True)
        
        # Create analytics dashboard
        print("Creating analytics...", flush=True)
        viz_data = self.create_network_analytics(entities, relationships, communities, centrality)
        
        # Group entities by community
        community_members = defaultdict(list)
        for entity, community_id in communities.items():
            community_members[community_id].append({
                'entity': entity,
                'type': entities[entity],
                'degree': centrality[entity]['degree'],
                'pagerank': centrality[entity]['pagerank']
            })
        
        # Sort members within each community by PageRank
        for comm_id in community_members:
            community_members[comm_id].sort(key=lambda x: x['pagerank'], reverse=True)
        
        # Group entities by community for detailed display
        community_members = {}
        for entity, community_id in communities.items():
            if community_id not in community_members:
                community_members[community_id] = []
            community_members[community_id].append({
                'entity': entity,
                'type': entities[entity],
                'degree': centrality[entity]['degree']
            })
        
        return {
            'network_path': os.path.basename(network_path),
            'entities': entities,
            'relationships': len(relationships),
            'relationship_details': relationships,
            'communities': communities,
            'community_members': community_members,
            'community_members': dict(community_members),  # NEW: detailed community info
            'centrality': centrality,
            'visualizations': viz_data
        }
    
    def create_network_analytics(self, entities: Dict[str, str], 
                                 relationships: List[Tuple[str, str, float]],
                                 communities: Dict[str, int],
                                 centrality: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Create analytics dashboard"""
        
        # Top entities by different measures
        top_by_degree = sorted(centrality.items(), key=lambda x: x[1]['degree'], reverse=True)[:10]
        top_by_pagerank = sorted(centrality.items(), key=lambda x: x[1]['pagerank'], reverse=True)[:10]
        
        # Community distribution
        community_counts = Counter(communities.values())
        
        # Create dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Top Entities by Connections',
                'Top Entities by PageRank',
                'Community Distribution',
                'Network Statistics'
            ),
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "pie"}, {"type": "indicator"}]
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.12
        )
        
        # Top by degree
        fig.add_trace(
            go.Bar(
                y=[e[0] for e in top_by_degree],
                x=[e[1]['degree'] for e in top_by_degree],
                orientation='h',
                marker=dict(color='#4ECDC4', line=dict(color='white', width=1)),
                text=[e[1]['degree'] for e in top_by_degree],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Connections: %{x}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Top by PageRank
        fig.add_trace(
            go.Bar(
                y=[e[0] for e in top_by_pagerank],
                x=[e[1]['pagerank'] for e in top_by_pagerank],
                orientation='h',
                marker=dict(color='#FF6B6B', line=dict(color='white', width=1)),
                text=[f"{e[1]['pagerank']:.4f}" for e in top_by_pagerank],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>PageRank: %{x:.4f}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Community distribution
        fig.add_trace(
            go.Pie(
                labels=[f'Community {i}' for i in sorted(community_counts.keys())],
                values=[community_counts[i] for i in sorted(community_counts.keys())],
                marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']),
                textinfo='label+value',
                hole=0.3
            ),
            row=2, col=1
        )
        
        # Network statistics
        avg_degree = np.mean([c['degree'] for c in centrality.values()]) if centrality else 0
        
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=len(entities),
                title={"text": f"Total Entities<br><span style='font-size:0.7em'>Avg Connections: {avg_degree:.1f}</span>"},
                number={'font': {'size': 48, 'color': '#2c3e50'}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            showlegend=False,
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            font=dict(family='Arial', size=12, color='#2c3e50'),
            title={
                'text': 'Network Analysis Dashboard',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#2c3e50'}
            },
            margin=dict(l=20, r=20, t=80, b=20)
        )
        
        fig.update_xaxes(title_text='Number of Connections', row=1, col=1)
        fig.update_xaxes(title_text='PageRank Score', row=1, col=2)
        
        return {
            'analytics_plot': json.loads(fig.to_json()),
            'stats': {
                'total_entities': len(entities),
                'total_relationships': len(relationships),
                'num_communities': len(community_counts),
                'avg_degree': avg_degree,
                'density': len(relationships) / (len(entities) * (len(entities) - 1) / 2) if len(entities) > 1 else 0
            }
        }
    
    def create_network(self, text: str, output_dir: str = '.') -> Dict[str, Any]:
        """Backward compatibility wrapper"""
        return self.create_network_graph(text, output_dir)