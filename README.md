# ice-ken

[![Release](https://github.com/vignirvignir/ice-ken/actions/workflows/release.yml/badge.svg)](https://github.com/vignirvignir/ice-ken/actions/workflows/release.yml)
[![CI](https://github.com/vignirvignir/ice-ken/actions/workflows/ci.yml/badge.svg)](https://github.com/vignirvignir/ice-ken/actions/workflows/ci.yml)

Python library for working with Icelandic national IDs (kennitala).

## Overview

Kennitala is a 10-digit identifier typically written as `DDMMYY-NNNX`:
- Digits 1–6: day, month, year (two digits)
- Digits 7–8: sequence
- Digit 9: Modulus 11 checksum (policy exception from 2026)
- Digit 10: century indicator (`8`→1800s, `9`→1900s, `0`→2000s)

Companies encode the day as `DD = actual_day + 40` (41–71). When resolving a date, subtract 40 from the day for company IDs.

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

print(is_valid(raw))                 # strict (checksum enforced)
print(is_valid(raw, enforce_checksum=False))  # relaxed

info = parse(raw)                    # raises on invalid (strict by default)
print(info.birth_date, info.entity_type)

print(mask(raw))                     # "******-3399"
print(is_company(raw), is_personal(raw))
```

## API Overview

- **`normalize(value)`**: return digits-only string.
- **`format_kennitala(value)`**: format as `DDMMYY-NNNX`.
- **`is_valid(value, enforce_checksum=True)`**: structural + date validation; optionally enforce checksum.
- **`parse(value, enforce_checksum=True)`**: return `ParsedKennitala` with `digits`, `formatted`, `birth_date`, `entity_type`, `century_indicator`.
- **`mask(value, visible_tail=4)`**: masked display keeping last digits.
- **`is_company(value)` / `is_personal(value)`**: entity detection.
- **`is_dataset_id(value)`**: test-only helper for synthetic dataset marker (`14`/`15` in digits 7–8).
- **Generators**: `generate_personal`, `generate_company`, plus date-specific variants and `random_*` helpers. All support `enforce_checksum` and `formatted` options.
- **`get_birth_date(value, enforce_checksum=True)`**: resolve the birth/registration date.

## Validation Modes

- **Strict**: enforce Modulus 11 (9th digit).
- **Relaxed**: skip checksum while enforcing structure and date.

```python
from ice_ken import is_valid

print(is_valid("120160-3389"))                         # True (passes checksum)
print(is_valid("120160-3379", enforce_checksum=False))  # True (relaxed)
print(is_valid("120160-3379"))                          # False (fails checksum)
```

Policy notice: From February 18, 2026, Registers Iceland may issue kennitalas without a computed checksum. Prefer relaxed validation when appropriate. Details in [docs/about-kennitala.md](docs/about-kennitala.md).

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

GNU General Public License v3.0 or later. See [LICENSE](LICENSE).
