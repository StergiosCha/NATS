# app/models/dimension_reducer.py update
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import numpy as np
import plotly.express as px
from typing import Dict, List, Union, Any

class DimensionReducer:
    def __init__(self, n_components: int = 2):
        self.n_components = n_components
        
    def reduce_embeddings(self, 
                         embeddings: Dict[str, np.ndarray], 
                         method: str = 'pca'
                         ) -> Dict[str, Any]:
        """
        Reduce embeddings (either word or document) to lower dimensions
        """
        # Convert embeddings to matrix
        labels = list(embeddings.keys())
        embedding_matrix = np.array([embeddings[label] for label in labels])
        
        # Perform dimension reduction
        if method.lower() == 'pca':
            reducer = PCA(n_components=min(self.n_components, len(labels)-1))
            reduced_matrix = reducer.fit_transform(embedding_matrix)
        else:  # t-SNE
            # Adjust perplexity based on number of samples
            perplexity = min(30, len(labels) - 1)
            reducer = TSNE(
                n_components=self.n_components, 
                perplexity=perplexity,
                n_iter=1000, 
                random_state=42
            )
            reduced_matrix = reducer.fit_transform(embedding_matrix)
        
        # Create visualization
        fig = px.scatter(
            x=reduced_matrix[:, 0],
            y=reduced_matrix[:, 1],
            text=labels,
            title=f'{method.upper()} Visualization'
        )
        
        fig.update_traces(
            textposition='top center',
            marker=dict(size=10)
        )
        
        # Get explained variance ratio for PCA
        explained_variance = None
        if method.lower() == 'pca':
            explained_variance = reducer.explained_variance_ratio_.tolist()
        
        return {
            'coordinates': reduced_matrix,
            'labels': labels,
            'plot': fig.to_json(),
            'explained_variance': explained_variance
        }
    
    def analyze_both_methods(self, embeddings: Dict[str, np.ndarray]) -> Dict[str, Dict]:
        """Run both PCA and t-SNE analysis"""
        return {
            'pca': self.reduce_embeddings(embeddings, 'pca'),
            'tsne': self.reduce_embeddings(embeddings, 'tsne')
        }
