# NATS - Natural Language Analysis & Text Suite

## Overview

NATS is an advanced text analysis platform featuring enhanced embeddings, sophisticated Named Entity Recognition (NER), and comprehensive network analysis. It's specifically optimized for Greek and multilingual content with modern React frontend and robust backend processing.

## Features

### 🚀 Enhanced Document Embeddings
- **Multiple Models**: Sentence Transformers, Doc2Vec
- **Advanced Preprocessing**: Text normalization, feature extraction
- **Dimension Reduction**: PCA, t-SNE, UMAP
- **Clustering**: K-means clustering with automatic cluster detection
- **Comprehensive Visualizations**: Multi-panel dashboards with similarity matrices

### 🎯 Advanced Named Entity Recognition
- **19 Entity Types**: PERSON, ORG, LOC, GPE, DATE, TIME, MONEY, PERCENT, etc.
- **Greek Language Support**: Custom regex patterns for Greek entities
- **Semantic Relationships**: Automatic relationship detection
- **Importance Scoring**: TF-IDF based entity importance calculation
- **Interactive Networks**: Dynamic entity relationship visualizations

### 🌐 Network Analysis
- **Community Detection**: Louvain algorithm for community identification
- **Centrality Measures**: Degree, betweenness, closeness centrality
- **Relationship Strength**: Co-occurrence and context-based scoring
- **Interactive Visualizations**: Physics-based network layouts
- **Comprehensive Analytics**: Network statistics and metrics

### 🎨 Modern Frontend
- **React-based**: Modern, responsive UI with Tailwind CSS
- **Real-time Analysis**: Live progress updates and notifications
- **Interactive Dashboards**: Plotly.js visualizations
- **File Upload**: Drag-and-drop interface with validation
- **Results Management**: Download results in JSON/CSV formats

## Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd NATS-1
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
python -m spacy download el_core_news_md
```

3. **Install and build frontend**
```bash
cd frontend
npm install
npm run build
cd ..
```

4. **Run the application**
```bash
python wsgi.py
```

The application will be available at `http://localhost:5000`

### Docker Deployment

1. **Build and run with Docker**
```bash
docker build -t nats-app .
docker run -p 5000:5000 nats-app
```

2. **Using Docker Compose**
```bash
docker-compose up --build
```

## Railway Deployment

### Prerequisites
- Railway account
- GitHub repository with your code

### Deployment Steps

1. **Connect to Railway**
   - Go to [Railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"

2. **Configure Environment Variables**
   ```
   PORT=5000
   FLASK_ENV=production
   PYTHONUNBUFFERED=1
   ```

3. **Deploy**
   - Select your repository
   - Railway will automatically detect the Python app
   - The deployment will use the provided `Dockerfile`

4. **Access Your App**
   - Railway will provide a public URL
   - Your NATS application will be live!

### Railway Configuration

The project includes:
- `railway.yml`: Railway-specific configuration
- `Dockerfile`: Optimized for Railway deployment
- Health check endpoint: `/api/health`
- Automatic frontend build in Docker

## API Endpoints

### Analysis
- `POST /api/analyze` - Upload files and perform analysis
- `GET /api/results/<analysis_id>` - Retrieve analysis results
- `GET /api/download/<analysis_id>` - Download results (JSON/CSV)

### Health & Static
- `GET /api/health` - Health check endpoint
- `GET /static/<filename>` - Serve static files

## Usage Examples

### Upload and Analyze Text Files

1. **Navigate to Upload Page**
   - Go to `/upload` in your browser
   - Select analysis type (Enhanced NER, Document Embeddings, Network Analysis, or Comprehensive)

2. **Upload Files**
   - Drag and drop `.txt` files or click to select
   - Configure analysis parameters
   - Click "Start Analysis"

3. **View Results**
   - Results page will show comprehensive analysis
   - Switch between tabs: Overview, Embeddings, Entities, Network
   - Download results in JSON or CSV format

### Analysis Types

- **Enhanced NER**: Advanced entity recognition with Greek support
- **Document Embeddings**: Multi-model embeddings with clustering
- **Network Analysis**: Community detection and centrality analysis
- **Comprehensive**: All analysis types combined

## Architecture

### Backend (Flask)
- **Enhanced Models**: Upgraded analyzers with advanced algorithms
- **RESTful API**: Clean API design with proper error handling
- **File Management**: Secure file upload and result storage
- **CORS Support**: Cross-origin requests for frontend integration

### Frontend (React)
- **Modern UI**: Tailwind CSS with responsive design
- **Component Architecture**: Modular React components
- **State Management**: React hooks for state management
- **Visualizations**: Plotly.js for interactive charts

### Data Processing
- **spaCy**: Advanced NLP processing
- **Sentence Transformers**: Multilingual embeddings
- **NetworkX**: Graph analysis and community detection
- **scikit-learn**: Machine learning algorithms

## Performance Optimization

### For Railway Free Tier
- **Memory Management**: Optimized model loading
- **File Size Limits**: 16MB max file size
- **Processing Limits**: Efficient algorithms for resource constraints
- **Caching**: Result caching to reduce computation

### Production Considerations
- **Scaling**: Horizontal scaling with multiple workers
- **Monitoring**: Health checks and logging
- **Security**: Input validation and secure file handling
- **Backup**: Result persistence and recovery

## Troubleshooting

### Common Issues

1. **spaCy Model Download**
   ```bash
   python -m spacy download el_core_news_md
   ```

2. **Frontend Build Issues**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

3. **Memory Issues on Railway**
   - Reduce file sizes
   - Use smaller embedding dimensions
   - Enable result caching

### Support

For issues and questions:
- Check the logs in Railway dashboard
- Review the health check endpoint
- Ensure all dependencies are installed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.







