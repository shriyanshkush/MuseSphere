# ==============================================================================
# Multi-Stage Dockerfile for MuseSphere API (Optimized for AWS Free Tier t2.micro)
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build & Dependencies (`builder`)
# ------------------------------------------------------------------------------
FROM python:3.12-slim as builder

WORKDIR /build

# Install system compilation dependencies required for psycopg and crypto libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment to isolate installed wheels cleanly
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install application dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ------------------------------------------------------------------------------
# Stage 2: Minimal Production Runtime (`runtime`)
# ------------------------------------------------------------------------------
FROM python:3.12-slim as runtime

WORKDIR /app

# Install runtime PostgreSQL client library and healthcheck curl utility
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-compiled virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create unprivileged non-root user for high security execution
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copy application source code and migration scripts
COPY . /app/
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Docker healthcheck probe verifying API endpoint responsiveness
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch uvicorn server with 2 workers tailored for AWS t2.micro (1 vCPU)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers"]
