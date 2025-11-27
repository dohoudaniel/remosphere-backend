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

COPY --from=builder /install /usr/local
COPY . .

# Create staticfiles directory
RUN mkdir -p /app/staticfiles

# Collect static at build time (MUCH faster)
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN useradd -u 1000 -ms /bin/bash appuser
USER appuser

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=remosphere.settings

# Final command
CMD ["gunicorn", "remosphere.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--log-level", "info"]
