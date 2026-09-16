from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def sample_forecast_payload() -> dict:
    return json.loads((FIXTURES_DIR / "sample_forecast_response.json").read_text())


@pytest.fixture()
def malformed_payload() -> dict:
    return json.loads((FIXTURES_DIR / "malformed_response.json").read_text())
