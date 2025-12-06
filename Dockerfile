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

# Download Spacy models
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download el_core_news_md

# Copy application code
COPY . .

# Run the application
# Workers=1 and Threads=2 for 512MB RAM optimization
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:80", "--workers", "1", "--threads", "2", "--timeout", "120"]
