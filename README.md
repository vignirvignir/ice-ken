# ice-ken

[![Release](https://github.com/vignirvignir/ice-ken/actions/workflows/release.yml/badge.svg)](https://github.com/vignirvignir/ice-ken/actions/workflows/release.yml)
[![CI](https://github.com/vignirvignir/ice-ken/actions/workflows/ci.yml/badge.svg)](https://github.com/vignirvignir/ice-ken/actions/workflows/ci.yml)

A Python library for validating, parsing, formatting, masking, and generating Icelandic national identification numbers (**kennitala** / **kennitölur**). Built for developers working with Icelandic identity systems, government registries, KYC/AML flows, or any application that handles Icelandic personal and company IDs.

Kennitala (plural: kennitölur) is Iceland's national ID system, issued by Registers Iceland (Þjóðskrá Íslands). It serves a similar role to SSN (US), personnummer (Nordics), or national ID numbers in other countries. Every individual and legal entity in Iceland has one.

## Why ice-ken?

- **Zero dependencies** — pure Python, nothing to install beyond the package itself.
- **Python 3.9–3.13** — tested across all supported versions.
- **2026-ready** — handles the Feb 2026 policy change where Registers Iceland may issue kennitalas without valid Modulus 11 checksums. Dual validation modes (strict and relaxed) let you choose.
- **Individuals and companies** — validates and distinguishes both personal IDs (kennitala einstaklinga) and company/legal entity IDs (kennitala lögaðila) using the day+40 rule.
- **Generation for testing** — create realistic, structurally valid kennitalas for tests, fixtures, and seed data without using real IDs.
- **Safe masking** — redact kennitalas for logs, UIs, and reports while preserving the format.
- **Typed** — ships with `py.typed` and full type annotations for mypy/pyright.

## Overview

Kennitala is a 10-digit identifier typically written as `DDMMYY-NNNX`:
- Digits 1–6: day (DD), month (MM), year (YY, two digits)
- Digits 7–8: sequence number
- Digit 9: Modulus 11 check digit (policy exception from Feb 2026)
- Digit 10: century indicator (`8`=1800s, `9`=1900s, `0`=2000s)

Companies and legal entities encode the day as `DD = actual_day + 40` (range 41–71). When resolving a date, subtract 40 from the day for company IDs.

See the full background and rules in [docs/about-kennitala.md](docs/about-kennitala.md).

## Install

```bash
python3 -m pip install ice-ken
```

For local development:

```bash
python3 -m pip install -e .
```

## Quick Start

```python
from ice_ken import normalize, format_kennitala, is_valid, parse, mask, is_company, is_personal

raw = "120174-3399"
digits = normalize(raw)              # "1201743399"
print(format_kennitala(digits))      # "120174-3399"

print(is_valid(raw))                 # relaxed (default since 2.0)
print(is_valid(raw, enforce_checksum=True))   # strict (checksum enforced)

info = parse(raw)                    # raises on invalid (relaxed by default)
print(info.birth_date, info.entity_type)

print(mask(raw))                     # "******-3399"
print(is_company(raw), is_personal(raw))
```

## API Overview

- **`normalize(value)`**: return digits-only string.
- **`format_kennitala(value)`**: format as `DDMMYY-NNNX`.
- **`is_valid(value, enforce_checksum=False)`**: structural + date validation; optionally enforce checksum.
- **`parse(value, enforce_checksum=False)`**: return `ParsedKennitala` with `digits`, `formatted`, `birth_date`, `entity_type`, `century_indicator`.
- **`mask(value, visible_tail=4)`**: masked display keeping last digits.
- **`is_company(value)` / `is_personal(value)`**: entity detection.
- **`is_dataset_id(value)`**: test-only helper for synthetic dataset marker (`14`/`15` in digits 7–8).
- **`generate_personal(birth_date=None, ...)`**: generate a personal kennitala, optionally for a specific date.
- **`generate_company(reg_date=None, ...)`**: generate a company kennitala, optionally for a specific date.
- **`generate_kennitala(kind, birth_date=None, ...)`**: unified generator for either type.
- **`generate_batch(count, kind, ...)`**: generate multiple kennitölur at once.
- **`get_birth_date(value, enforce_checksum=False)`**: resolve the birth/registration date.
- Additional aliases: `generate_personal_for_date`, `generate_company_for_date`, `random_personal`, `random_company`.

## Validation Modes

- **Relaxed** (default): validates structure, date, and century indicator. Skips checksum.
- **Strict**: additionally enforces Modulus 11 checksum (9th digit).

```python
from ice_ken import is_valid

print(is_valid("120160-3389"))                          # True (relaxed, default)
print(is_valid("120160-3379"))                          # True (relaxed, bad checksum ok)
print(is_valid("120160-3379", enforce_checksum=True))   # False (strict, fails checksum)
```

Since February 18, 2026, Registers Iceland issues kennitalas without a computed checksum. The default relaxed mode accepts these IDs. Use `enforce_checksum=True` only when you need to verify the checksum for pre-2026 IDs. Details in [docs/about-kennitala.md](docs/about-kennitala.md).

## Companies vs Individuals

- Personal IDs: `DD` in `01–31` (calendar day).
- Company IDs: `DD` in `41–71` (day + 40).

```python
from ice_ken import is_company, is_personal

print(is_personal("120160-3389"))   # True
print(is_company("520160-3379"))    # True (company: 52 → day 12)
```

## Synthetic Dataset Marker

For test contexts, Registers Iceland’s synthetic dataset (Gervigögn) uses `14` or `15` in digits 7–8:

```python
from ice_ken import is_dataset_id
print(is_dataset_id("120160-1489"))  # True
```

Do not rely on this marker in production logic.

## Generation

Generate structurally valid kennitölur for testing, seeding databases, or any scenario where you need realistic IDs.

```python
from datetime import date
from ice_ken import (
    generate_personal,
    generate_company,
    generate_kennitala,
    generate_batch,
)

# Random personal kennitala (checksum-valid, formatted)
kt = generate_personal()              # e.g. "120585-2389"

# Personal kennitala for a specific birth date
kt = generate_personal(birth_date=date(1990, 5, 20))  # encodes 20-05-90

# Normalized (digits only) output
kt = generate_personal(formatted=False)     # e.g. "1205852389"

# Random company kennitala
kt = generate_company()               # e.g. "520312-2190"

# Company kennitala for a specific registration date
kt = generate_company(reg_date=date(2015, 3, 12))

# Unified entry point
kt = generate_kennitala("personal", target_date=date(1985, 1, 1))
kt = generate_kennitala("company")

# Batch generation — 100 random personal IDs
batch = generate_batch(100)

# Batch of company IDs, all sharing a date
batch = generate_batch(50, "company", target_date=date(2020, 6, 1))

# Relaxed mode: structurally valid but checksum intentionally wrong
kt = generate_personal(enforce_checksum=False)
```

All generators accept `enforce_checksum` (default `True`) and `formatted` (default `True`).

## Documentation

- Structure, checksum, century rules: [docs/about-kennitala.md](docs/about-kennitala.md)
- System-level notes: [docs/system-kennitala.md](docs/system-kennitala.md)
- Data files: [docs/data-files.md](docs/data-files.md)
- Vocabulary: [docs/vocabulary.md](docs/vocabulary.md)

## Development

Requirements: Python 3.9+

```bash
# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install package and test tools
python3 -m pip install --upgrade pip
python3 -m pip install -e .
python3 -m pip install pytest

# Run tests
python3 -m pytest -q

# Optional: run the XML loader on sample data
python3 -m ice_ken.loaders data/Thjordska-Gervigogn-VartolulausarKennitolur.xml
```

## CI & Release

- GitHub Actions run tests on Python 3.9–3.13 (see [\.github/workflows/ci.yml](.github/workflows/ci.yml)).
- Releases use `python-semantic-release` to version from Conventional Commits and publish to PyPI via OIDC (see [\.github/workflows/release.yml](.github/workflows/release.yml)).
- PR titles and commits are linted for Conventional Commits (see [\.github/workflows/semantic-pr.yml](.github/workflows/semantic-pr.yml) and [\.commitlintrc.json](.commitlintrc.json)).

## Contributing

We welcome contributions—bug fixes, improvements, documentation, tests, and new helpers. If something can make working with kennitalas safer or clearer, please propose it.

Guidelines:
- Keep changes focused and well-tested.
- Use Conventional Commits for messages.
- Add/extend tests for new behavior.
- Update docs when APIs or behavior change.
- Open a PR to `main` from a feature branch; CI must be green.

For agent and repository workflow details, see [AGENTS.md](AGENTS.md).

## License

MIT License. See [LICENSE](LICENSE).
