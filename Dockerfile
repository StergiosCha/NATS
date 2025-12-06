# Dockerfile for Render (Backend Only)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Spacy models (Direct URL to avoid 404s)
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
RUN pip install https://github.com/explosion/spacy-models/releases/download/el_core_news_md-3.7.0/el_core_news_md-3.7.0-py3-none-any.whl

# Copy application code
COPY . .

# Run the application
# Workers=1 and Threads=2 for 512MB RAM optimization
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:80", "--workers", "1", "--threads", "2", "--timeout", "120"]
