# syntax=docker/dockerfile:1
#
# Iris classifier: reproducible ML research service.
# Follows "Ten simple rules for writing Dockerfiles for reproducible data
# science" (Nüst et al., 2020, doi:10.1371/journal.pcbi.1008316):
# pinned base image and package versions, documented, cache-friendly order,
# one-click runnable.
#
# Build:  docker build -t iris-classifier .
# Run:    docker run --rm -p 8000:8000 iris-classifier
# Test:   curl http://localhost:8000/health

ARG PYTHON_VERSION=3.12

# ---------- Stage 1: build dependencies and train the model ----------
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dependencies first: this layer is cached until requirements.txt changes
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt

# Source code and data
COPY src/ src/
COPY data/ data/

# Train inside the image: the model is built from the exact code and data
# in this commit. The build fails if accuracy is below the quality gate.
RUN PYTHONPATH=src python -m iris_classifier.train --out models --min-accuracy 0.90

# ---------- Stage 2: minimal runtime image ----------
FROM python:${PYTHON_VERSION}-slim AS runtime

ARG VCS_REF=unknown
ARG BUILD_DATE=unknown
LABEL org.opencontainers.image.title="iris-classifier" \
      org.opencontainers.image.description="Iris species classifier (UCI dataset, DOI 10.24432/C56C76) served as a REST API" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.licenses="MIT"

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    MODEL_DIR=/app/models

WORKDIR /app

# Run as a non-root user
RUN useradd --create-home --uid 10001 appuser

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/src ./src
COPY --from=builder /app/data ./data
COPY --from=builder /app/models ./models

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "iris_classifier.wsgi:app"]
