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
