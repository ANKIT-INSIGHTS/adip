# ADIP runtime image.
# Builds and runs the pipeline with no external credentials required —
# Open-Meteo needs no API key.

FROM python:3.11-slim AS base

# System deps: git is required because change_detection.py shells out to
# `git show` to compare candidate outputs against the last committed version.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (better layer caching): only re-installs when
# pyproject.toml changes, not on every source edit.
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[dev]" 2>/dev/null || true

COPY . .
RUN pip install --no-cache-dir -e .

# Non-root user for defense in depth.
RUN useradd --create-home --shell /bin/bash adip \
    && chown -R adip:adip /app
USER adip

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "scripts/run_pipeline.py"]
CMD []
