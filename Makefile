.PHONY: install test lint format typecheck pipeline rebuild-db report clean docker-build docker-run

VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check src scripts tests

format:
	$(PY) -m ruff format src scripts tests
	$(PY) -m ruff check --fix src scripts tests

typecheck:
	$(PY) -m mypy src

pipeline:
	$(PY) scripts/run_pipeline.py

rebuild-db:
	$(PY) scripts/rebuild_db.py

report: pipeline
	@echo "Report written to reports/latest_report.md"

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache .ruff_cache data/snapshots/adip.duckdb
	find . -name "__pycache__" -type d -exec rm -rf {} +

docker-build:
	docker build -t adip:latest .

docker-run:
	docker run --rm -v $(PWD)/data:/app/data -v $(PWD)/reports:/app/reports adip:latest
