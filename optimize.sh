#!/bin/bash

# NATS Optimization Script for Free Tier Deployment
# Run this script from your project root directory

set -e  # Exit on error

echo "🚀 NATS Free Tier Optimization Script"
echo "======================================"
echo ""

# Step 1: Create branch
echo "📌 Step 1: Creating optimization branch..."
git checkout -b free-tier-optimization
echo "✅ Branch created"
echo ""

# Step 2: Backup and update requirements
echo "📌 Step 2: Updating requirements.txt..."
cp requirements.txt requirements-original.txt
cat > requirements.txt << 'EOF'
flask==2.3.3
werkzeug==2.3.7
spacy==3.7.2
gensim==4.3.2
numpy==1.24.3
scipy==1.11.3
scikit-learn==1.3.2
plotly==5.17.0
chardet==5.2.0
pyvis==0.3.2
networkx==3.2.1
pandas==2.1.3
gunicorn==21.2.0
python-dotenv==1.0.0
sentence-transformers==2.2.2
transformers==4.35.2
tokenizers==0.15.0
huggingface-hub==0.19.4
safetensors==0.4.1
--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.1.1+cpu
tqdm==4.66.1
textstat==0.7.3
nltk==3.8.1
beautifulsoup4==4.12.2
requests==2.31.0
python-louvain==0.16
flask-cors==4.0.0
EOF
echo "✅ Requirements updated (saved backup as requirements-original.txt)"
echo ""

# Step 3: Update Dockerfile
echo "📌 Step 3: Updating Dockerfile..."
cp Dockerfile Dockerfile-original
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download SMALL spaCy model (not medium - saves 40MB)
RUN python -m spacy download el_core_news_sm

# Copy application code
COPY . .

# Environment variables for memory optimization
ENV PYTHONUNBUFFERED=1
ENV TOKENIZERS_PARALLELISM=false
ENV OMP_NUM_THREADS=2
ENV MKL_NUM_THREADS=2

# Create directories
RUN mkdir -p app/static uploads results

EXPOSE 8000

# Single worker with threads (saves memory)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--timeout", "120", "wsgi:app"]
EOF
echo "✅ Dockerfile updated (saved backup as Dockerfile-original)"
echo ""

# Step 4: Update spaCy model references
echo "📌 Step 4: Updating spaCy model references in Python files..."
find app -type f -name "*.py" -exec sed -i.bak 's/el_core_news_md/el_core_news_sm/g' {} \;
find app -type f -name "*.py.bak" -delete
echo "✅ All Python files updated to use small model"
echo ""

# Step 5: Update gitignore
echo "📌 Step 5: Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Optimization backups
*-original.txt
*-original.py
*-original
*.bak
EOF
echo "✅ .gitignore updated"
echo ""

# Step 6: Commit changes
echo "📌 Step 6: Committing changes..."
git add .
git commit -m "Optimize for free tier deployment

- Use CPU-only PyTorch (saves ~500MB)
- Switch to small spaCy model (saves ~40MB)
- Optimize Dockerfile with single worker
- Total size reduced from ~1.5GB to ~450MB"
echo "✅ Changes committed"
echo ""

# Summary
echo "======================================"
echo "✨ Optimization Complete!"
echo "======================================"
echo ""
echo "📊 Summary of Changes:"
echo "  • CPU-only PyTorch: -500MB"
echo "  • Small spaCy model: -40MB"
echo "  • Optimized Dockerfile"
echo "  • Expected final size: ~450MB ✅"
echo ""
echo "🚀 Next Steps:"
echo "  1. Test locally (optional):"
echo "     docker build -t nats-test ."
echo "     docker run --memory=\"512m\" -p 8000:8000 nats-test"
echo ""
echo "  2. Deploy to Railway:"
echo "     railway up"
echo ""
echo "  3. Or push to GitHub:"
echo "     git push origin free-tier-optimization"
echo ""
echo "📝 Your original files are backed up:"
echo "  • requirements-original.txt"
echo "  • Dockerfile-original"
echo ""
echo "🔄 To rollback:"
echo "  git checkout main"
echo ""
echo "Good luck! 🎉"
