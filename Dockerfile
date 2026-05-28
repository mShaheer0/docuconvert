# Multi-stage build for minimal image size
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies for PDF/Word conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only (smaller image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Create temp directory for file uploads
RUN mkdir -p /tmp/uploads

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start both nginx and gunicorn
CMD ["sh", "-c", "nginx -g 'daemon off;' & gunicorn backend.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 --access-logfile - --error-logfile - --log-level info"]
