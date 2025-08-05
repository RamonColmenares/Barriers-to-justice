# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for scipy and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY api/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/

# Copy main entry point
COPY main.py .

# Expose port 5000
EXPOSE 5000

# Set environment variables for optimized memory usage
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MALLOC_ARENA_MAX=2

# Run the application with Gunicorn - optimized for t3.small (2GB RAM)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--worker-class", "gthread", "--timeout", "300", "--keep-alive", "30", "--max-requests", "200", "--max-requests-jitter", "20", "--worker-tmp-dir", "/dev/shm", "--preload", "api.index:app"]
