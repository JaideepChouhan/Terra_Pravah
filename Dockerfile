# ================================================================
# Terra Pravah - Backend Dockerfile
# Professional Drainage Network Analysis Platform
# Production-Ready for Railway/Vercel Deployment
# ================================================================

FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    build-essential \
    gcc \
    g++ \
    # GDAL and geospatial libraries
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    # Image processing
    libjpeg-dev \
    libpng-dev \
    # Other dependencies
    curl \
    wget \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Create app user for security
RUN groupadd -r terrapravah && useradd -r -g terrapravah terrapravah

# Set work directory
WORKDIR /app

# Install WhiteboxTools
RUN wget -q https://www.whiteboxgeo.com/WBT_Linux/WhiteboxTools_linux_amd64.zip \
    && unzip -q WhiteboxTools_linux_amd64.zip -d /opt/ \
    && rm WhiteboxTools_linux_amd64.zip \
    && chmod +x /opt/WBT/whitebox_tools \
    && ln -s /opt/WBT/whitebox_tools /usr/local/bin/whitebox_tools

# Set WhiteboxTools path
ENV WBT_PATH=/opt/WBT

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn gevent gevent-websocket

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /tmp/uploads /tmp/results database logs \
    && chown -R terrapravah:terrapravah /app \
    && chown -R terrapravah:terrapravah /tmp/uploads \
    && chown -R terrapravah:terrapravah /tmp/results

# Create .gitkeep files
RUN touch /tmp/uploads/.gitkeep /tmp/results/.gitkeep

# Switch to non-root user
USER terrapravah

# Expose port (Railway uses PORT env var)
EXPOSE 5000

# Production Start Command
# Using gunicorn with gevent for WebSocket support
CMD ["gunicorn", \
     "-w", "4", \
     "-b", "0.0.0.0:5000", \
     "-k", "geventwebsockethandler", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "backend.app:app"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command
CMD ["gunicorn", "--factory", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "120", "backend.app:create_app"]
