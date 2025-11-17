# app/models/doc_embeddings.py
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
try:
    import umap
    UMAP_AVAILABLE = True
except:
    UMAP_AVAILABLE = False
    print("UMAP not available - using PCA/t-SNE only")
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import spacy
import pandas as pd
from typing import Dict, Any, List, Tuple
import re
import json
from collections import Counter

try:
    import textstat
    textstat.flesch_reading_ease("test")
    TEXTSTAT_AVAILABLE = True
except (ImportError, Exception):
    TEXTSTAT_AVAILABLE = False

class EnhancedDocEmbeddingAnalyzer:
    def __init__(self):
        """Initialize with multiple embedding models and preprocessing tools"""
        self.nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
        self.nlp.add_pipe('sentencizer')
        
        try:
            self.sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        except:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.vector_size = 100
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better embedding quality"""
        text = re.sub(r'\s+', ' ', text.strip())
        text = text.replace('΄', "'").replace('΅', '"')
        return text
    
    def extract_text_features(self, text: str) -> Dict[str, Any]:
        """Extract various text features"""
        doc = self.nlp(text)
        
        words = [token.text for token in doc if token.is_alpha]
        sentences = list(doc.sents)
        
        readability_score = 0
        if len(words) > 0 and len(sentences) > 0:
            if TEXTSTAT_AVAILABLE and len(text) > 100:
                try:
                    readability_score = textstat.flesch_reading_ease(text)
                except:
                    avg_sentence_length = len(words) / len(sentences)
                    avg_syllables = sum(max(1, len(word) // 3) for word in words) / len(words)
                    readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
                    readability_score = max(0, min(100, readability_score))
            else:
                avg_sentence_length = len(words) / len(sentences)
                avg_syllables = sum(max(1, len(word) // 3) for word in words) / len(words)
                readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
                readability_score = max(0, min(100, readability_score))
        
        return {
            'word_count': len([token for token in doc if not token.is_punct and not token.is_space]),
            'sentence_count': len(list(doc.sents)),
            'avg_word_length': np.mean([len(token.text) for token in doc if not token.is_punct]) if len([token for token in doc if not token.is_punct]) > 0 else 0,
            'readability_score': readability_score,
            'lexical_diversity': len(set(token.text.lower() for token in doc if token.is_alpha)) / max(1, len([token for token in doc if token.is_alpha])),
            'pos_distribution': dict(Counter([token.pos_ for token in doc if not token.is_punct]))
        }
    
    def create_embeddings(self, texts: Dict[str, str]) -> Dict[str, np.ndarray]:
        """Create sentence transformer embeddings - clean and simple"""
        embeddings = {}
        
        for filename, text in texts.items():
            # Process full text, no artificial balancing
            sentences = [sent.text for sent in self.nlp(text).sents if len(sent.text.strip()) > 10]
            
            if sentences:
                # Use all sentences for accurate representation
                embeddings_array = self.sentence_model.encode(sentences[:100])  # Cap at 100 sentences for memory
                embeddings[filename] = np.mean(embeddings_array, axis=0)
        
        return embeddings
    
    def reduce_dimensions(self, embeddings: np.ndarray, method: str = 'pca', n_components: int = 2) -> np.ndarray:
        """Reduce dimensions using various methods"""
        if len(embeddings) == 1:
            return np.array([[0.0, 0.0]])
        
        max_components = min(n_components, len(embeddings), embeddings.shape[1])
        max_components = max(2, max_components)
        
        try:
            if method == 'pca':
                reducer = PCA(n_components=max_components)
            elif method == 'tsne':
                perplexity = min(30, max(5, len(embeddings)-1))
                reducer = TSNE(n_components=max_components, perplexity=perplexity, random_state=42)
            elif method == 'umap':
                if not UMAP_AVAILABLE:
                    reducer = PCA(n_components=max_components)
                else:
                    reducer = umap.UMAP(n_components=max_components, random_state=42)
            else:
                reducer = PCA(n_components=max_components)
            
            result = reducer.fit_transform(embeddings)
            
            if result.shape[1] == 1:
                result = np.column_stack([result, np.zeros(len(result))])
            
            return result
            
        except Exception as e:
            print(f"Dimension reduction failed: {e}")
            return embeddings[:, :2] if embeddings.shape[1] >= 2 else np.column_stack([embeddings[:, 0], np.zeros(len(embeddings))])
    
    def cluster_embeddings(self, embeddings: np.ndarray, n_clusters: int = None) -> np.ndarray:
        """Cluster documents based on embeddings"""
        if len(embeddings) == 1:
            return np.array([0])
        
        if n_clusters is None:
            n_clusters = min(5, max(2, len(embeddings) // 2))
        
        if len(embeddings) < n_clusters:
            return np.zeros(len(embeddings), dtype=int)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        return kmeans.fit_predict(embeddings)
    
    def create_main_scatter_plot(self, coords: np.ndarray, filenames: List[str], 
                                clusters: np.ndarray, features: Dict[str, Dict]) -> go.Figure:
        """Create clean, interactive scatter plot"""
        
        # Color palette for clusters
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                 '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
        
        # Prepare hover data
        hover_text = []
        for fname in filenames:
            feat = features[fname]
            text = f"<b>{fname}</b><br>"
            text += f"Words: {feat['word_count']:,}<br>"
            text += f"Sentences: {feat['sentence_count']:,}<br>"
            text += f"Readability: {feat['readability_score']:.0f}/100<br>"
            text += f"Lexical Diversity: {feat['lexical_diversity']:.2f}"
            hover_text.append(text)
        
        # Create figure
        fig = go.Figure()
        
        # Add scatter points by cluster for better legend
        unique_clusters = sorted(set(clusters))
        for cluster_id in unique_clusters:
            mask = clusters == cluster_id
            cluster_coords = coords[mask]
            cluster_names = [filenames[i] for i, m in enumerate(mask) if m]
            cluster_hover = [hover_text[i] for i, m in enumerate(mask) if m]
            
            fig.add_trace(go.Scatter(
                x=cluster_coords[:, 0],
                y=cluster_coords[:, 1],
                mode='markers+text',
                name=f'Cluster {cluster_id}',
                text=cluster_names,
                textposition='top center',
                textfont=dict(size=11, color='white', family='Arial Black'),
                marker=dict(
                    size=16,
                    color=colors[cluster_id % len(colors)],
                    line=dict(width=2, color='white'),
                    opacity=0.9
                ),
                hovertext=cluster_hover,
                hoverinfo='text'
            ))
        
        fig.update_layout(
            title={
                'text': 'Document Embedding Space',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#2c3e50'}
            },
            xaxis_title='Principal Component 1',
            yaxis_title='Principal Component 2',
            height=600,
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            font=dict(family='Arial', size=12, color='#2c3e50'),
            hovermode='closest',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='#dee2e6',
                borderwidth=1
            ),
            margin=dict(l=60, r=180, t=80, b=60)
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#dee2e6', zeroline=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#dee2e6', zeroline=False)
        
        return fig
    
    def create_features_chart(self, filenames: List[str], features: Dict[str, Dict]) -> go.Figure:
        """Create clean features comparison chart"""
        
        # Prepare data
        word_counts = [features[f]['word_count'] for f in filenames]
        sentence_counts = [features[f]['sentence_count'] for f in filenames]
        readability = [features[f]['readability_score'] for f in filenames]
        diversity = [features[f]['lexical_diversity'] * 100 for f in filenames]  # Scale to 0-100
        
        fig = go.Figure()
        
        # Add traces
        fig.add_trace(go.Bar(
            name='Words (÷100)',
            x=filenames,
            y=[w/100 for w in word_counts],
            marker_color='#4ECDC4',
            hovertemplate='<b>%{x}</b><br>Words: %{customdata:,}<extra></extra>',
            customdata=word_counts
        ))
        
        fig.add_trace(go.Bar(
            name='Sentences (÷10)',
            x=filenames,
            y=[s/10 for s in sentence_counts],
            marker_color='#45B7D1',
            hovertemplate='<b>%{x}</b><br>Sentences: %{customdata:,}<extra></extra>',
            customdata=sentence_counts
        ))
        
        fig.add_trace(go.Scatter(
            name='Readability',
            x=filenames,
            y=readability,
            mode='lines+markers',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=10),
            yaxis='y2',
            hovertemplate='<b>%{x}</b><br>Readability: %{y:.0f}/100<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': 'Document Features Comparison',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#2c3e50'}
            },
            xaxis_title='Documents',
            yaxis_title='Count (scaled)',
            yaxis2=dict(
                title='Readability Score',
                overlaying='y',
                side='right',
                range=[0, 100]
            ),
            height=450,
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            barmode='group',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=60, r=60, t=80, b=100)
        )
        
        fig.update_xaxes(tickangle=45, showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#dee2e6')
        
        return fig
    
    def create_similarity_heatmap(self, embedding_matrix: np.ndarray, filenames: List[str]) -> go.Figure:
        """Create clean similarity heatmap"""
        
        # Calculate cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarity_matrix = cosine_similarity(embedding_matrix)
        
        # Create custom hover text
        hover_text = []
        for i, fname1 in enumerate(filenames):
            row = []
            for j, fname2 in enumerate(filenames):
                if i == j:
                    row.append(f"<b>{fname1}</b><br>Self")
                else:
                    row.append(f"<b>{fname1}</b> ↔ <b>{fname2}</b><br>Similarity: {similarity_matrix[i,j]:.3f}")
            hover_text.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=similarity_matrix,
            x=filenames,
            y=filenames,
            colorscale='Blues',
            text=hover_text,
            hoverinfo='text',
            colorbar=dict(
                title='Similarity',
                tickmode='linear',
                tick0=0,
                dtick=0.2
            )
        ))
        
        fig.update_layout(
            title={
                'text': 'Document Similarity Matrix',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#2c3e50'}
            },
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=100, r=120, t=80, b=100)
        )
        
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    def create_comprehensive_visualization(self, texts: Dict[str, str], 
                                         embedding_type: str = 'sentence_transformer',
                                         reduction_method: str = 'pca') -> Dict[str, Any]:
        """Create comprehensive visualization with clean, separated plots"""
        
        # Extract features
        features = {filename: self.extract_text_features(text) for filename, text in texts.items()}
        
        # Create embeddings (simplified - no artificial balancing)
        embeddings = self.create_embeddings(texts)
        
        if not embeddings:
            return {'error': 'No embeddings could be created'}
        
        filenames = list(embeddings.keys())
        embedding_matrix = np.array([embeddings[fname] for fname in filenames])
        
        # Reduce dimensions
        coords = self.reduce_dimensions(embedding_matrix, reduction_method)
        
        # Cluster documents
        clusters = self.cluster_embeddings(embedding_matrix)
        
        # Create three separate, clean visualizations
        scatter_plot = self.create_main_scatter_plot(coords, filenames, clusters, features)
        features_chart = self.create_features_chart(filenames, features)
        similarity_heatmap = self.create_similarity_heatmap(embedding_matrix, filenames)
        
        # Return as parsed dicts, not JSON strings
        return {
            'scatter_plot': json.loads(scatter_plot.to_json()),
            'features_chart': json.loads(features_chart.to_json()),
            'similarity_heatmap': json.loads(similarity_heatmap.to_json()),
            'embeddings': {fname: emb.tolist() for fname, emb in embeddings.items()},
            'features': features,
            'clusters': {fname: int(cluster) for fname, cluster in zip(filenames, clusters)},
            'filenames': filenames
        }