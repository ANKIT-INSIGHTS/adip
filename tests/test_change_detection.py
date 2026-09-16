from __future__ import annotations

import json
from pathlib import Path

from adip.change_detection import canonicalize, content_hash
from adip.config import ChangeDetectionConfig

CFG = ChangeDetectionConfig(
    float_comparison_decimals=2,
    ignore_json_keys=("generationtime_ms", "retrieved_at"),
)


def test_canonicalize_strips_ignored_keys(tmp_path: Path):
    path = tmp_path / "a.json"
    path.write_text(json.dumps({"value": 1, "generationtime_ms": 12.34}))
    canon = canonicalize(path, CFG)
    assert b"generationtime_ms" not in canon
    assert b'"value": 1' in canon


def test_canonicalize_rounds_float_noise(tmp_path: Path):
    path_a = tmp_path / "a.json"
    path_b = tmp_path / "b.json"
    path_a.write_text(json.dumps({"temp": 21.999999999998}))
    path_b.write_text(json.dumps({"temp": 22.0000000000001}))
    assert canonicalize(path_a, CFG) == canonicalize(path_b, CFG)


def test_content_hash_identical_for_semantically_equal_files(tmp_path: Path):
    path_a = tmp_path / "a.json"
    path_b = tmp_path / "b.json"
    path_a.write_text(json.dumps({"temp": 21.001, "retrieved_at": "2026-01-01T00:00:00Z"}))
    path_b.write_text(json.dumps({"temp": 21.002, "retrieved_at": "2026-06-01T12:00:00Z"}))
    assert content_hash(path_a, CFG) == content_hash(path_b, CFG)


def test_content_hash_differs_for_real_change(tmp_path: Path):
    path_a = tmp_path / "a.json"
    path_b = tmp_path / "b.json"
    path_a.write_text(json.dumps({"temp": 21.0}))
    path_b.write_text(json.dumps({"temp": 25.0}))
    assert content_hash(path_a, CFG) != content_hash(path_b, CFG)


def test_canonicalize_normalizes_line_endings_in_markdown(tmp_path: Path):
    path_a = tmp_path / "a.md"
    path_b = tmp_path / "b.md"
    path_a.write_bytes(b"line one\r\nline two\r\n")
    path_b.write_bytes(b"line one\nline two\n")
    assert canonicalize(path_a, CFG) == canonicalize(path_b, CFG)


def test_binary_file_hashed_by_raw_bytes(tmp_path: Path):
    path = tmp_path / "chart.png"
    path.write_bytes(b"\x89PNG\r\n fake bytes")
    # Should not raise even though it's not valid JSON/text.
    h = content_hash(path, CFG)
    assert len(h) == 64
