# Stage 1: Builder
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

RUN apt-get clean && rm -rf /var/lib/apt/lists/* && \
    for i in 1 2 3; do \
        apt-get update --allow-releaseinfo-change && \
        apt-get install -y --no-install-recommends \
            build-essential \
            libpq-dev \
            curl && break || sleep 5; \
    done && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: Final image
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install supervisor and runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        supervisor \
        libpq5 && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/log/supervisor

COPY --from=builder /install /usr/local
COPY . .

# Copy supervisor config and startup script
COPY supervisord.conf /app/supervisord.conf
COPY start.sh /app/start.sh

# Make start script executable
RUN chmod +x /app/start.sh

# Create necessary directories
RUN mkdir -p /app/staticfiles && chown -R 1000:1000 /app/staticfiles
RUN useradd -u 1000 -ms /bin/bash appuser

# Note: Supervisor runs as root to manage processes, but Django and Celery run as appuser
# USER appuser

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=remosphere.settings
ENV STATIC_ROOT=/app/staticfiles

CMD ["/app/start.sh"]
