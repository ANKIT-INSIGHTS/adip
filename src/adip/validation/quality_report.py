"""Write reports/data_quality/latest.json and latest.md from CheckResult lists."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from adip.config import REPO_ROOT
from adip.validation.quality_checks import CheckResult

QUALITY_DIR = REPO_ROOT / "reports" / "data_quality"


def write_quality_report(checks_by_city: dict[str, list[CheckResult]]) -> tuple[Path, Path]:
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(UTC).isoformat()

    all_checks: list[dict[str, Any]] = []
    for city_id, checks in checks_by_city.items():
        for c in checks:
            entry = c.to_dict()
            entry["city_id"] = city_id
            all_checks.append(entry)

    total = len(all_checks)
    passed = sum(1 for c in all_checks if c["passed"])
    payload = {
        "generated_at": generated_at,
        "total_checks": total,
        "passed": passed,
        "failed": total - passed,
        "overall_status": "pass" if passed == total else "fail",
        "checks": all_checks,
    }
    json_path = QUALITY_DIR / "latest.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Data Quality Report",
        "",
        f"_Generated: {generated_at}_",
        "",
        f"**Overall status:** "
        f"{'✅ PASS' if payload['overall_status'] == 'pass' else '❌ FAIL'} "
        f"({passed}/{total} checks passed)",
        "",
        "| City | Check | Passed | Measured | Threshold | Detail |",
        "|---|---|---|---|---|---|",
    ]
    for check_entry in all_checks:
        lines.append(
            f"| {check_entry['city_id']} | {check_entry['name']} | "
            f"{'✅' if check_entry['passed'] else '❌'} | "
            f"{check_entry['measured_value']} | {check_entry['threshold']} | "
            f"{check_entry['detail']} |"
        )
    md_path = QUALITY_DIR / "latest.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path
