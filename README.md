# NATS - Narrative Analysis & Text System

NATS is a comprehensive text analysis tool that combines Named Entity Recognition (NER), Document Embeddings, and Network Analysis to provide deep insights into textual data. It features a Flask backend and a React frontend.

## 🚀 Features

*   **Enhanced NER**: Extracts entities with specialized support for Greek language and morphology.
*   **Document Embeddings**: Semantic analysis using Sentence Transformers (optimized for memory).
*   **Network Analysis**: Interactive visualization of entity relationships, communities, and centrality.
*   **Interactive Dashboard**: Modern React-based UI for easy file upload and result exploration.

## 📂 Project Structure

*   `app/`: Main backend application code (Optimized for Render/Low-RAM environments).
*   `app_backup_v1/`: Backup of the original backend code (before memory optimizations).
*   `frontend/`: React frontend application.
*   `wsgi.py`: Entry point for the Flask application.
*   `run_app.sh`: Helper script to set up the environment and run the backend.

## 🛠️ Installation & Running

### Prerequisites
*   Python 3.11+
*   Node.js & npm

### Quick Start (Backend)

We provide a script to automatically set up the Python virtual environment and dependencies:

```bash
./run_app.sh
```

This will:
1.  Create a `venv` (using Python 3.11).
2.  Install requirements.
3.  Download necessary Spacy models.
4.  Start the Flask server on port `8052`.

### Quick Start (Frontend)

Open a new terminal window:

```bash
cd frontend
npm install
npm start
```

The application will be available at `http://localhost:3000`.

## ☁️ Deployment (Render.com)

This application has been optimized to run on Render's **Free Tier (512MB RAM)**.

**Key Optimizations:**
*   **Lazy Loading**: Heavy AI models (Spacy, Transformers) are only loaded into memory when a specific analysis is requested.
*   **Smaller Models**: Switched to `all-MiniLM-L6-v2` for embeddings to save ~300MB RAM compared to the standard model.
*   **Chunk Processing**: Large texts are processed in chunks to prevent memory spikes.

**Build Command:**
```bash
pip install -r requirements.txt && python -m spacy download en_core_web_sm && python -m spacy download el_core_news_md
```

**Start Command:**
```bash
gunicorn wsgi:app --bind 0.0.0.0:$PORT
```

## 📝 License

[Your License Here]
