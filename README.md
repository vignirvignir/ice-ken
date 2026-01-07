# ice-ken

[![Release](https://github.com/vignirvignir/ice-ken/actions/workflows/release.yml/badge.svg)](https://github.com/vignirvignir/ice-ken/actions/workflows/release.yml)
[![CI](https://github.com/vignirvignir/ice-ken/actions/workflows/ci.yml/badge.svg)](https://github.com/vignirvignir/ice-ken/actions/workflows/ci.yml)

Utilities for managing Icelandic national IDs (kennitala) safely and efficiently.

## Features

- Modern Python packaging with pyproject.toml
- `src/` layout for clean imports
- Python 3.9+ compatible
- Normalize, format, validate, and mask kennitala

## Installation

Install from PyPI (once published):

```bash
python3 -m pip install ice-ken
```

Install locally for development:

```bash
python3 -m pip install -e .
```

## Usage

```python
from ice_ken import __version__, normalize, is_valid, parse, format_kennitala, mask, is_company, is_personal

raw = "120174-3399"
digits = normalize(raw)                # "1201743399"
formatted = format_kennitala(digits)   # "120174-3399"
valid = is_valid(raw)                  # True/False (strict: checksum enforced)
valid_relaxed = is_valid(raw, enforce_checksum=False)  # True/False (relaxed)
masked = mask(raw)                     # "******-3399"
print(is_company(raw), is_personal(raw))  # e.g., False True

if valid:
 info = parse(raw)
 print(info.birth_date)             # datetime.date(...)

# Parse in relaxed mode (skip checksum enforcement)
info_relaxed = parse("120160-3379", enforce_checksum=False)
print(info_relaxed.formatted)
```

## Validation Modes

- Strict: `is_valid(value)` enforces the Modulus 11 check digit (9th digit).
- Relaxed: `is_valid(value, enforce_checksum=False)` skips the check digit while still enforcing structure and date.

Example:

```python
from ice_ken import is_valid

print(is_valid("120160-3389"))                         # True (passes checksum)
print(is_valid("120160-3379", enforce_checksum=False))  # True (ignores checksum)
print(is_valid("120160-3379"))                          # False (fails checksum)
```

## Companies vs Individuals

- Personal IDs: `DD` in `01–31` (calendar day)
- Company/legal entity IDs: `DD` in `41–71` (day + 40 rule)

Quick checks:

```python
from ice_ken import is_company, is_personal

print(is_personal("120160-3389"))   # True
print(is_company("520160-3379"))    # True (company: 52 → day 12)
```

## Generate Test IDs

Create random kennitalas for development and testing:

```python
from ice_ken import generate_personal, generate_company, is_valid

# Personal (strict checksum)
kt_person = generate_personal()                 # e.g., "DDMMYY-NNNX"
print(is_valid(kt_person))                      # True

# Personal (relaxed, checksum not enforced)
kt_person_relaxed = generate_personal(enforce_checksum=False)
print(is_valid(kt_person_relaxed, enforce_checksum=False))  # True

# Company (strict checksum)
kt_company = generate_company()
print(is_valid(kt_company))                      # True

# Company (relaxed)
kt_company_relaxed = generate_company(enforce_checksum=False)
print(is_valid(kt_company_relaxed, enforce_checksum=False))  # True

# Get raw 10-digit form instead of formatted
raw_digits = generate_personal(formatted=False)  # e.g., "DDMMYYNNNPC"
```

### Synthetic Dataset Helper

Registers Iceland's synthetic dataset (Gervigögn) distinguishes test kennitalas by placing `14` or `15` in positions 7–8. For test-only detection, use:

```python
from ice_ken import is_dataset_id

print(is_dataset_id("120160-1489"))  # True
print(is_dataset_id("120160-3389"))  # False
```

Note: This is a dataset convention for testing; do not rely on it in production.

## Documentation

For a detailed explanation of kennitala structure, century and checksum rules, and policy notes, see [docs/about-kennitala.md](docs/about-kennitala.md).

### Policy Notice (February 18, 2026)

Registers Iceland will begin issuing kennitalas without a computed Modulus 11 check digit starting Feb 18, 2026. After this date, prefer relaxed validation (`enforce_checksum=False`) unless business requirements mandate the legacy parity check. See [docs/about-kennitala.md](docs/about-kennitala.md) for details and testing guidance.

## Contributing

Contributions are welcome and encouraged! This project aims to provide reliable, well-tested utilities for working with Icelandic kennitalas.

### How to Contribute

1. **Fork the repository** and create your feature branch
2. **Follow the development setup** in [AGENTS.md](AGENTS.md)
3. **Add tests** for any new functionality
4. **Follow Conventional Commits** for commit messages
5. **Submit a Pull Request** — all PRs are reviewed by the repository owner

### What We're Looking For

- **Bug fixes and improvements** to existing functionality
- **Additional validation helpers** and utilities
- **Documentation enhancements** and examples
- **Test coverage improvements** and edge cases
- **Performance optimizations**
- **Support for additional use cases**

### Guidelines

- Keep changes focused and well-documented
- Ensure all tests pass before submitting
- Add tests for new features or bug fixes
- Update documentation when changing APIs
- Follow the existing code style and patterns

We value all contributions, from typo fixes to major features. The Icelandic tech community benefits when we build robust, open-source tools together!

## License

This project is licensed under the GNU General Public License v3.0 or later — see the LICENSE file for details.
