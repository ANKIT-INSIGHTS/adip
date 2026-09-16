# Self-Audit

This document records the pre-delivery review of ADIP: real bugs found and
fixed during development, a systematic failure-point review, and gaps that
remain genuinely open (not papered over).

## Bugs found and fixed during development

Development included actually executing every piece of logic that didn't
require a package unavailable in the authoring sandbox (`pandas`, `numpy`,
and stdlib were available; `duckdb`, `pydantic`, and `pytest` were not, and
no network access was available to install them). This caught two real,
non-cosmetic bugs that a purely visual code review would likely have missed:

1. **`descriptive.rolling_average` silently returned all-`NaN`.**
   `groupby(...).rolling(window, on=series)` requires `on` to be a column
   *name* (string), not the Series object itself — passing the Series
   raised `ValueError` on the version installed, and a plausible-looking
   variant of the same mistake would have silently misaligned results on
   other pandas versions via the MultiIndex the operation returns. Fixed
   by grouping/sorting explicitly and assigning results by position
   (verified safe because both sides share the same sort order). Covered
   by `test_rolling_average_correct_per_group_alignment`, which checks
   *values*, not just "did it run" — a weaker test would have passed on
   the broken version too, since NaN doesn't raise.

2. **Two SQL `INSERT` statements had fewer `?` placeholders than their
   target table's column count** (`current_conditions`: 8 vs. 9;
   `observed_weather`: 8 vs. 9, in both `scripts/run_pipeline.py` and
   `scripts/rebuild_db.py`). This would have raised a runtime error the
   first time either code path executed with real data — i.e., on the
   very first city with a `current` block, and the first time archive data
   was ingested. Found by writing a script that parses `schema.sql` and
   every `INSERT` statement and diffs placeholder count against column
   count; that script is now `tests/test_sql_consistency.py`, a permanent
   regression guard that runs without needing DuckDB installed.

3. **Timezone-naive/aware datetime mismatch.** `datetime.now(timezone.utc)`
   (aware) was being stored directly into DuckDB `TIMESTAMP` columns
   (naive), which risked silent join/comparison failures downstream (e.g.
   `.isin()` checks between aware and naive datetimes, or DuckDB's Python
   driver rejecting/mishandling tz-aware input depending on version). Fixed
   by normalizing to naive UTC once, in `transformation/normalize.py`,
   before any timestamp enters a DataFrame destined for storage.

## Systematic failure-point review

| # | Problem | Likelihood | Impact | Prevention | Fallback |
|---|---|---|---|---|---|
| 1 | Dependency install fails in CI (version conflict) | Low | Pipeline never runs | Pinned version ranges in `pyproject.toml`; `tests.yml` installs fresh on every push/PR | Dependabot PRs surface conflicts early; fix pin and re-run |
| 2 | SQL placeholder/column mismatch (class of bug #2 above) | Was High, now Low | Runtime crash, exit 2, no commit | `test_sql_consistency.py` static check | Pipeline fails loudly rather than writing malformed rows |
| 3 | pandas API drift across versions (class of bug #1 above) | Medium | Silently wrong analytics, no crash | Value-checking regression tests, not just "did it run" | Pin pandas major version range |
| 4 | Open-Meteo renames/removes a response field | Low–Medium (years) | `OpenMeteoSchemaError` raised | Pydantic schema validates every response | Pipeline fails cleanly (exit 2); fix `schemas.py`, redeploy |
| 5 | Archive data lags real time | Certain, by design | Very recent forecasts can't be scored | `archive.min_days_lag` config | Documented as expected behavior, not a defect |
| 6 | DuckDB rebuild time grows with raw-file count | Eventual, at scale | Slower CI runs, could approach timeout | None yet — documented as a known scaling limit | Raise `timeout-minutes`, or implement incremental rebuild |
| 7 | Overlapping workflow runs race on git push | Low (schedule spacing) | Push conflict, job failure | `concurrency` group with `cancel-in-progress` | Next scheduled run recovers automatically |
| 8 | `git push` rejected (remote moved between checkout and push) | Low | Job fails | Concurrency control shrinks the window | **Not fully mitigated** — see Open Gaps below |
| 9 | matplotlib version bump changes chart bytes with no data change | Medium, over time | One "spurious" commit | Documented tradeoff | Accepted as one-time noise, not recurring |
| 10 | Open-Meteo rate-limits at current city count | Low | 429s, handled via backoff | Retry + backoff + self-throttle | City skipped for this run; retried next cycle |
| 11 | Open-Meteo fully down | Low | All cities fail | `cities_succeeded == 0` returns exit 2 | Job fails loudly (red X in Actions), no commit, no fabricated data |
| 12 | Partial city failures (transient network blips) | Medium | Some cities missing this cycle | Per-city try/except isolation | Report shows `partial_failure` status honestly; retried next cycle |
| 13 | Bot commits don't appear on personal contribution graph | Certain, by design | Reviewer might expect green squares | Explicitly documented (README + `docs/architecture.md`) | Reviewer checks commit log / Actions tab instead |
| 14 | Timezone mismatch (class of bug #3 above) | Was High, now Low | Silent join/comparison errors | Normalized to naive UTC at the transformation boundary | No fallback needed; verified by manual trace |
| 15 | `data/raw/` grows unbounded over months of history | Certain, gradual | Repo size grows | None implemented | **Open gap** — see below |
| 16 | Type errors slip through despite `mypy` | Low–Medium | Caught late, or not at all | `mypy` runs informationally in CI; `ruff` catches many real errors | Accepted tradeoff, documented in README Limitations |
| 17 | Logic paths never executed in this sandbox (no `duckdb`/`pydantic`/`pytest`) | Was certain here | Latent bugs possible beyond the two found | Manual trace-through + full execution of every pandas/numpy-only path | **CI is the real gate** — `tests.yml` runs the full suite with real dependencies on every push/PR before anything merges |
| 18 | Secrets accidentally committed | Low (none are needed at all) | N/A | `.gitignore` excludes `.env`/`*.pem`/`*.key`; `trufflehog` secret-scan in `security.yml` | Rotate immediately if it ever happens (not applicable — no secrets exist) |
| 19 | Dependabot bump breaks main if merged blindly | Medium, over time | Broken `main` | `tests.yml` runs on every Dependabot PR too | Manual review before merge; PRs are not set to auto-merge |
| 20 | GitHub Actions cron fires late/skips under platform load | Known GitHub behavior | Slightly irregular cadence | `workflow_dispatch` available for manual catch-up | Accepted — not something any repo can control |
| 21 | Chart function crashes on all-NaN/empty data | Low–Medium | Unhandled exception mid-run | Every chart function checks `.empty`/returns `None` before plotting | Verified by code review of `reporting/charts.py` |
| 22 | Duplicate raw snapshot files from rapid re-runs | Very low | Harmless redundant files | Snapshot filenames are second-precision timestamps | Change detection treats them as legitimately new content, not an error |

## Open gaps (not resolved, stated plainly)

- **#8, git push race on remote-ahead-of-local:** the workflow does not
  currently `git pull --rebase` before pushing. At a 6-hour schedule with
  `concurrency: cancel-in-progress`, the realistic window for this is very
  small, but it is not zero (e.g., a human pushing directly to `main` at
  the exact moment a scheduled run is pushing). If this becomes a real
  problem, the fix is a `git pull --rebase origin main` step immediately
  before `git push` in `pipeline.yml`.
- **#15, unbounded raw-data growth:** no retention/archival policy exists
  yet. At 16 cities × 4 runs/day × small JSON files, this is not a near-term
  problem, but it is explicitly not solved, only sized up as low-risk for
  the project's realistic lifetime. Documented in the README's Future
  Improvements as the natural next step (alongside incremental DB rebuild,
  which has the same root cause).
- **#17, sandbox execution limits:** this repository's logic was validated
  as thoroughly as the authoring environment allowed (full execution of
  every pandas/numpy-pure code path, static SQL consistency checking, and
  manual trace-through of pydantic/DuckDB-dependent code), but was not
  executed end-to-end with real `duckdb`+`pydantic`+`pytest` before
  delivery, because the authoring sandbox had no network access to install
  them. This is why `tests.yml`'s first real run in your GitHub account is
  not a formality — treat a red X there as a genuine, expected-possible
  signal, not noise, and fix forward from whatever it reports.

## Answers to the standard pre-delivery checklist

- **Runs from a clean clone?** Yes, modulo the caveat in gap #17 above:
  `make install && make test` is the actual first verification, not this
  document's word for it.
- **Imports valid, dependencies complete?** Verified via `py_compile` on
  every file and manual import-graph review; not verified via a real
  `pip install` in this sandbox (no network).
- **Paths cross-platform?** All paths built with `pathlib.Path`; no raw
  string path concatenation anywhere in `src/` or `scripts/`.
- **Workflows syntactically valid YAML?** Hand-reviewed structurally; not
  run through GitHub's own validator (only possible once pushed).
- **Permissions correct/minimal?** Yes — see the README's GitHub Actions
  table; no workflow uses `write-all`.
- **API failures handled safely?** Yes — retries, backoff, timeouts, and a
  hard refusal to fabricate data on failure (`OpenMeteoError` propagates).
- **Idempotent (two runs, identical data, no diff)?** Yes for the
  canonicalization logic itself (verified directly). Full end-to-end
  idempotency additionally depends on DuckDB/pydantic behaving as expected
  (gap #17).
- **Timestamps normalized?** Yes — naive UTC throughout storage (bug #3
  fix), and `change_detection` additionally strips/rounds volatile fields
  regardless.
- **Tests actually test useful behavior?** Yes — value assertions, not
  just "does it run" (see bug #1's regression test as the model).
- **Reports based on real data, no fabricated metrics?** Yes — the report
  builder does no computation, only formatting of values computed
  elsewhere; every number is traceable to a specific analytics function.
- **Security vulnerabilities / hardcoded credentials?** None — Open-Meteo
  needs no credentials; `security.yml` runs `pip-audit`, `trufflehog`, and
  CodeQL on a schedule and on every push/PR.
- **Commits meaningful?** Yes, by construction of the change-detection
  layer — see the README's "Intelligent commit system" section.
- **Docker / local / scheduled execution all work?** Docker and local
  execution use the identical `scripts/run_pipeline.py` entrypoint;
  scheduled execution runs the same script via `pipeline.yml`. Not
  independently verified with a live `docker build` in this sandbox (no
  network to pull the base image).
- **Does the README accurately describe the implementation?** Yes,
  including one correction made specifically for this reason: the
  architecture diagrams originally implied tests run *inside* the pipeline
  script after reporting; they actually run as an earlier, separate CI
  step. Both `README.md` and `docs/architecture.md` were corrected to
  state this precisely rather than leave the more flattering but
  inaccurate version.
