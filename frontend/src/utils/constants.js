// API Routes
export const API_ROUTES = {
  ANALYZE: '/api/analyze',
  RESULTS: '/api/results',
  DOWNLOAD: '/api/download',
  ANALYSES: '/api/analyses',
  HEALTH: '/api/health'
};

// Analysis Types
export const ANALYSIS_TYPES = {
  NER: 'enhanced_ner',
  EMBEDDINGS: 'enhanced_embeddings',
  NETWORK: 'enhanced_network',
  COMPREHENSIVE: 'comprehensive'
};

// Embedding Types
export const EMBEDDING_TYPES = {
  SENTENCE_TRANSFORMER: 'sentence_transformer',
  DOC2VEC: 'doc2vec'
};

// Reduction Methods
export const REDUCTION_METHODS = {
  PCA: 'pca',
  TSNE: 'tsne',
  UMAP: 'umap'
};

// File Upload Constraints
export const FILE_UPLOAD = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: ['.txt'],
  MIME_TYPES: ['text/plain']
};

// Toast Messages
export const TOAST_MESSAGES = {
  UPLOAD_SUCCESS: 'Analysis completed successfully!',
  UPLOAD_ERROR: 'Upload failed. Please try again.',
  DOWNLOAD_SUCCESS: 'Results downloaded successfully!',
  DOWNLOAD_ERROR: 'Failed to download results',
  FILE_ADDED: (count) => `${count} file(s) added`,
  FILE_REJECTED: 'Only .txt files are allowed',
  NO_FILES: 'Please select at least one file',
  RESULTS_ERROR: 'Failed to load results'
};

// Color Classes for Tailwind (safe for dynamic use)
export const COLOR_CLASSES = {
  blue: {
    bg: 'bg-blue-100',
    text: 'text-blue-600',
    icon: 'text-blue-600',
    border: 'border-blue-400'
  },
  green: {
    bg: 'bg-green-100',
    text: 'text-green-600',
    icon: 'text-green-600',
    border: 'border-green-400'
  },
  purple: {
    bg: 'bg-purple-100',
    text: 'text-purple-600',
    icon: 'text-purple-600',
    border: 'border-purple-400'
  },
  orange: {
    bg: 'bg-orange-100',
    text: 'text-orange-600',
    icon: 'text-orange-600',
    border: 'border-orange-400'
  },
  red: {
    bg: 'bg-red-100',
    text: 'text-red-600',
    icon: 'text-red-600',
    border: 'border-red-400'
  },
  yellow: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-600',
    icon: 'text-yellow-600',
    border: 'border-yellow-400'
  }
};

// Plotly Chart Config
export const PLOTLY_CONFIG = {
  responsive: true,
  displaylogo: false,
  displayModeBar: true,
  modeBarButtonsToRemove: ['lasso2d', 'select2d'],
  toImageButtonOptions: {
    format: 'png',
    height: 1200,
    width: 1600,
    scale: 2
  }
};

// Default Chart Layout
export const DEFAULT_CHART_LAYOUT = {
  autosize: true,
  margin: { l: 60, r: 60, t: 80, b: 60 },
  font: {
    family: 'Inter, system-ui, sans-serif',
    size: 12,
    color: '#2c3e50'
  },
  plot_bgcolor: '#f8f9fa',
  paper_bgcolor: 'white'
};

// Tab Configurations
export const RESULTS_TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'embeddings', label: 'Embeddings' },
  { id: 'entities', label: 'Entities' },
  { id: 'network', label: 'Network' }
];