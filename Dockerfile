# ============================================
# STAGE 1: Builder
# ============================================
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install to a virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# STAGE 2: Runtime
# ============================================
FROM python:3.12-slim

# Set environment variables globally
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install runtime dependencies only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Copy and make entrypoint executable
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Healthcheck for the API container
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
  CMD sh -c 'curl -fsS "http://127.0.0.1:${PORT:-8000}/health/db" || exit 1'

# Entrypoint and default command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

# Create non-root user
RUN adduser --disabled-password --no-create-home appuser

# Set ownership
RUN chown -R appuser:appuser /app

# Switch user
USER appuser
