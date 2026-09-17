"""Decide whether a pipeline run produced a *meaningful* change worth
committing.

This is the core of ADIP's "intelligent commit system." The rule is simple
and non-negotiable: a commit happens only if canonicalized, volatility-
stripped output actually differs from what's already in git. Running the
pipeline twice against identical upstream data must be a no-op.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from adip.config import REPO_ROOT, ChangeDetectionConfig

_FLOAT_RE = re.compile(r"-?\d+\.\d+")


@dataclass(slots=True)
class ChangeReport:
    changed_files: list[str]
    unchanged_files: list[str]
    has_meaningful_change: bool


def _round_floats_in_text(text: str, decimals: int) -> str:
    """Round every float literal in a text blob to `decimals` places so that
    float noise (e.g. 21.999999999998 vs 22.0) never triggers a commit.
    """

    def _round_match(m: re.Match) -> str:
        return f"{float(m.group()):.{decimals}f}"

    return _FLOAT_RE.sub(_round_match, text)


def _strip_ignored_keys(obj, ignore_keys: set[str]):
    if isinstance(obj, dict):
        return {
            k: _strip_ignored_keys(v, ignore_keys)
            for k, v in obj.items()
            if k not in ignore_keys
        }
    if isinstance(obj, list):
        return [_strip_ignored_keys(v, ignore_keys) for v in obj]
    return obj


def canonicalize(path: Path, cfg: ChangeDetectionConfig) -> bytes:
    """Produce a canonical byte representation of a file for hashing:
    strips volatile keys (JSON only), rounds floating point noise, and
    normalizes line endings. Binary files (e.g. PNG) are hashed by raw bytes
    with no normalization — chart regeneration is only "meaningful" if the
    actual pixels differ, which for our deterministic-DPI matplotlib output
    correlates well enough with real data changes.
    """
    raw = path.read_bytes()
    if path.suffix == ".json":
        try:
            obj = json.loads(raw.decode("utf-8"))
            obj = _strip_ignored_keys(obj, set(cfg.ignore_json_keys))
            text = json.dumps(obj, sort_keys=True, indent=2)
            text = _round_floats_in_text(text, cfg.float_comparison_decimals)
            return text.encode("utf-8")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return raw
    if path.suffix in {".md", ".txt"}:
        text = raw.decode("utf-8", errors="replace")
        text = _round_floats_in_text(text, cfg.float_comparison_decimals)
        text = text.replace("\r\n", "\n")
        return text.encode("utf-8")
    return raw


def content_hash(path: Path, cfg: ChangeDetectionConfig) -> str:
    return hashlib.sha256(canonicalize(path, cfg)).hexdigest()


def _git_show(path: Path) -> bytes | None:
    """Return the last-committed bytes of a path, or None if untracked."""
    rel = path.relative_to(REPO_ROOT)
    result = subprocess.run(  # noqa: S603
        ["git", "show", f"HEAD:{rel.as_posix()}"],  # noqa: S607
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def detect_changes(candidate_paths: list[Path], cfg: ChangeDetectionConfig) -> ChangeReport:
    """Compare each candidate output path's canonical hash against the
    canonical hash of the version currently committed in git.
    """
    changed, unchanged = [], []
    for path in candidate_paths:
        if not path.exists():
            continue
        new_hash = content_hash(path, cfg)

        previous_bytes = _git_show(path)
        if previous_bytes is None:
            changed.append(str(path.relative_to(REPO_ROOT)))
            continue

        tmp_path = path.parent / f"{path.stem}.prev_tmp{path.suffix}"
        tmp_path.write_bytes(previous_bytes)
        try:
            old_hash = content_hash(tmp_path, cfg)
        finally:
            tmp_path.unlink(missing_ok=True)

        if new_hash == old_hash:
            unchanged.append(str(path.relative_to(REPO_ROOT)))
        else:
            changed.append(str(path.relative_to(REPO_ROOT)))

    return ChangeReport(
        changed_files=changed,
        unchanged_files=unchanged,
        has_meaningful_change=len(changed) > 0,
    )
