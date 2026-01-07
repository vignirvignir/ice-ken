# AGENTS — Operating Guide for LLM Contributors

This document defines how autonomous agents should work on this repository with minimal human intervention. Follow these rules strictly: never commit directly to `main`, adhere to Conventional Commits, keep changes focused, and ensure the test suite passes.

## Project Overview

- Purpose: `ice-ken` is a Python library for working with Icelandic national IDs (kennitala).
- Core module: `src/ice_ken/kennitala.py` provides helpers to:
  - normalize input (`normalize`),
  - format IDs (`format_kennitala`),
  - validate IDs in strict or relaxed mode (`is_valid(value, enforce_checksum=...)`),
  - parse structured info (`parse`) returning `ParsedKennitala` with `birth_date`, `entity_type`, etc.,
  - mask for safe display (`mask`),
  - entity detection (`is_company`, `is_personal`),
  - test dataset marker detection (`is_dataset_id`),
  - generate test IDs (`generate_personal`, `generate_company`).
- Loaders: `src/ice_ken/loaders.py` parses sample XML and validates records, producing metadata (`validation.relaxed/strict`, `entity_type`, `birth_date`).
- Documentation: see [docs/about-kennitala.md](docs/about-kennitala.md) for structure, checksum rules, and 2026 policy (relaxed checksum acceptance). Additional docs in [docs/](docs).

## Local Environment & Commands

- Requirements: Python 3.9+.
- Set up environment and install editable package with dev tools:

```bash
# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package and dependencies
python3 -m pip install --upgrade pip
python3 -m pip install -e .
python3 -m pip install pytest
```

- Run tests:

```bash
python3 -m pytest -q
```

- Run XML loader test manually (optional sanity):

```bash
python3 -m ice_ken.loaders data/Thjordska-Gervigogn-VartolulausarKennitolur.xml
```

- Build distributions locally:

```bash
python3 -m build
```

## CI & Release

- CI: [CI workflow](.github/workflows/ci.yml) runs tests on Python 3.9–3.13.
- Release: [release workflow](.github/workflows/release.yml)
  - Uses `python-semantic-release` to derive next version from Conventional Commits, update [pyproject.toml](pyproject.toml) and [CHANGELOG.md](CHANGELOG.md), tag, and create a GitHub Release.
  - Publishes to PyPI via Trusted Publishing (OIDC) using `pypa/gh-action-pypi-publish`. No `PYPI_TOKEN` required once configured on PyPI.
  - For pull requests targeting `main`, a TestPyPI job builds and publishes to TestPyPI (OIDC) to validate packaging.
- PR Title Lint: [semantic-pr.yml](.github/workflows/semantic-pr.yml) enforces Conventional Commit style for PR titles.
- Commit Message Lint: [commitlint.yml](.github/workflows/commitlint.yml) validates commit messages against Conventional Commits.
- Badges: see [README.md](README.md) for CI/Release status.

## Conventional Commits — Mandatory

Agents must write commit messages and PR titles in Conventional Commits format. See guidance in [\.copilot-commit-message-instructions.md](.copilot-commit-message-instructions.md) and rules in [\.commitlintrc.json](.commitlintrc.json).

- Header format: `<type>(<scope>): <description>`
- Type (lower-case, required): one of `feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert`.
- Scope (lower-case, required): pick a concise module or area (e.g., `kennitala`, `tests`, `ci`).
- Description: lower-case verb phrase, no trailing period.
- Breaking changes: use `!` after the type (e.g., `feat!: ...`) or add a `BREAKING CHANGE:` footer.
- Body/footer: start after one blank line.
- Max header length: 72 chars.

Examples:

```commit
feat(kennitala): add relaxed parsing examples in docs

* docs: expand checksum policy notes
```

```commit
fix(tests): correct company day extremes in property tests

BREAKING CHANGE: none
```

## Branching & PR Workflow — Never Commit to main

- Create a feature branch from `main` (e.g., `feat/kennitala-relaxed-mode-docs`).
- Push commits to the branch; ensure Conventional Commit messages.
- Open a Pull Request targeting `main` with a Conventional Commit–style title.
- Ensure CI is green (tests pass across all Python versions).
- Do not bump versions manually; semantic-release handles versioning on `push` to `main`.
- Merges to `main` will trigger the Release pipeline and publish to PyPI via OIDC.

## Versioning Semantics

- Semantic release infers the next version from commit history:
  - `feat`: minor bump.
  - `fix`: patch bump.
  - `BREAKING CHANGE` or `!`: major bump.
  - Others (`docs`, `test`, etc.) typically do not change the version unless configured otherwise.
- The authoritative version lives in [pyproject.toml](pyproject.toml) under `project.version`; do not edit manually.

## Operating Checklist for Agents

1. Read project docs: [docs/about-kennitala.md](docs/about-kennitala.md) and API in `src/ice_ken/kennitala.py`.
2. Run tests locally: `python3 -m pytest -q` and ensure green before proposing changes.
3. Implement focused changes:
   - Keep edits minimal and consistent with existing style.
   - Prefer root-cause fixes; avoid unrelated refactors.
4. Add/extend tests in `tests/` to cover new behavior, following current patterns (unit tests + property tests in `tests/test_properties.py`).
5. Update docs in `docs/` if APIs or behavior change.
6. Commit with Conventional Commits (required scope) and push to a feature branch.
7. Open PR to `main` with a Conventional Commit–style title; ensure CI passes.
8. After merge, the Release workflow will bump version, create the GitHub Release, and publish to PyPI via Trusted Publishing.

## Coding & Testing Notes

- Validation modes:
  - Strict (`is_valid(value)`): enforces Modulus 11 checksum.
  - Relaxed (`is_valid(value, enforce_checksum=False)`): ignores checksum per 2026 policy.
- Company IDs: day field stored as `DD = actual_day + 40` (41–71); parsing subtracts 40 when resolving `birth_date`.
- Century indicator (10th digit): `8`→1800s, `9`→1900s, `0`→2000s.
- Dataset marker helper: `is_dataset_id` checks positions 7–8 for `14` or `15` (for official synthetic dataset only; do not use in production logic).
- Property tests: `tests/test_properties.py` fuzzes dates/sequences for personal/company and verifies strict vs relaxed behavior.
- Loader:
  - `parse_einstaklingar_xml()` ingests sample XML and maps fields.
  - `validate_records()` annotates relaxed/strict validity, dataset marker, entity type, and resolved birth date.

## Security & Compliance

- Do not introduce dependencies with restrictive licenses without approval.
- Do not commit secrets; CI uses OIDC for PyPI.
- Respect privacy: dataset files under `data/` are synthetic.

## Quick Reference

- Key files:
  - Library: [src/ice_ken/kennitala.py](src/ice_ken/kennitala.py)
  - Loaders: [src/ice_ken/loaders.py](src/ice_ken/loaders.py)
  - Tests: [tests/](tests/)
  - CI: [\.github/workflows/ci.yml](.github/workflows/ci.yml)
  - Release: [\.github/workflows/release.yml](.github/workflows/release.yml)
  - Commitlint: [\.github/workflows/commitlint.yml](.github/workflows/commitlint.yml), [\.commitlintrc.json](.commitlintrc.json)
  - PR title lint: [\.github/workflows/semantic-pr.yml](.github/workflows/semantic-pr.yml)
  - Config: [pyproject.toml](pyproject.toml)

Adhering to this guide ensures agents can contribute safely and efficiently, with automated tests, versioning, and releases handled by CI.
