from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import numpy as np
import plotly.express as px
from typing import Dict, Any

class DimensionReducer:
    def __init__(self, n_components: int = 2):
        self.n_components = n_components
        
    def reduce_dimensions(self, 
                         embeddings: Dict[str, np.ndarray], 
                         method: str = 'pca'
                         ) -> Dict[str, Any]:
        """Reduce dimensions of embeddings"""
        # Prepare data
        labels = list(embeddings.keys())
        embedding_matrix = np.array([embeddings[label] for label in labels])
        
        # Choose reducer
        if method.lower() == 'pca':
            reducer = PCA(n_components=min(self.n_components, len(labels)-1))
        else:  # t-SNE
            perplexity = min(30, max(5, len(labels) // 5))
            reducer = TSNE(
                n_components=self.n_components,
                perplexity=perplexity,
                n_iter=250,
                random_state=42
            )
        
        # Reduce dimensions
        reduced = reducer.fit_transform(embedding_matrix)
        
        # Create visualization
        fig = px.scatter(
            x=reduced[:, 0],
            y=reduced[:, 1],
            text=labels,
            title=f'{method.upper()} Visualization'
        )
        
        fig.update_traces(
            textposition='top center',
            marker=dict(size=10)
        )
        
        return {
            'coordinates': reduced.tolist(),
            'labels': labels,
            'plot': fig.to_json()
        }
    
    def analyze_both(self, embeddings: Dict[str, np.ndarray]) -> Dict[str, Dict]:
        """Run both PCA and t-SNE"""
        return {
            'pca': self.reduce_dimensions(embeddings, 'pca'),
            'tsne': self.reduce_dimensions(embeddings, 'tsne')
        }
