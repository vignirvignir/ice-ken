# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`ice-ken` is a Python library (published to PyPI) for working with Icelandic national IDs (kennitala). Pure Python, no runtime dependencies. Requires Python 3.9+.

## Commands

```bash
# Install (editable)
python3 -m pip install -e .

# Run all tests
python3 -m pytest -q

# Run a single test file
python3 -m pytest tests/test_kennitala.py -q

# Run a single test by name
python3 -m pytest -k "test_name" -q

# Run XML loader on sample data
python3 -m ice_ken.loaders data/Thjordska-Gervigogn-VartolulausarKennitolur.xml

# Build distribution
python3 -m build
```

## Architecture

Source lives in `src/ice_ken/` (src layout via setuptools):

- **`kennitala.py`** — All core logic: `normalize`, `format_kennitala`, `is_valid`, `parse` (returns `ParsedKennitala` dataclass), `mask`, `is_company`, `is_personal`, `is_dataset_id`, and generation helpers (`generate_personal`, `generate_company`). Two validation modes: strict (Modulus 11 checksum enforced) and relaxed (`enforce_checksum=False`).
- **`loaders.py`** — XML parser for Registers Iceland synthetic dataset files. Parses records and annotates with validation metadata.
- **`__init__.py`** — Re-exports public API from `kennitala.py`.

Tests in `tests/`:
- `test_kennitala.py` — Unit tests for core functions.
- `test_properties.py` — Property-based tests fuzzing dates/sequences for personal and company IDs.
- `test_generation.py` — Tests for ID generation helpers.
- `test_loader.py` — Tests for XML loader.

## Domain Rules

- Kennitala: 10-digit ID formatted as `DDMMYY-NNNX`.
- Company IDs: day field = actual day + 40 (range 41-71). Subtract 40 when resolving dates.
- Century indicator (10th digit): `8`=1800s, `9`=1900s, `0`=2000s.
- Dataset marker: digits 7-8 are `14` or `15` for synthetic test data.
- From Feb 2026, Registers Iceland may issue kennitalas without valid checksums. Prefer relaxed validation (`enforce_checksum=False`) when appropriate.

## Commit & PR Conventions

Conventional Commits are **enforced by CI** (commitlint + semantic-pr workflows). Scope is required.

Format: `<type>(<scope>): <description>`

Types: `feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert`

Examples:
- `feat(kennitala): add batch validation helper`
- `fix(tests): correct company day boundary assertion`

Never commit directly to `main`. Create a feature branch and open a PR. Semantic-release handles versioning on merge to `main`.

## CI & Release

- CI tests on Python 3.9-3.13 (`.github/workflows/ci.yml`).
- `python-semantic-release` bumps version in `pyproject.toml`, updates `CHANGELOG.md`, tags, and publishes to PyPI via OIDC on merge to `main`.
- Do not edit `project.version` in `pyproject.toml` manually.
