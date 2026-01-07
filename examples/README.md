# Examples for ice-ken

This folder contains copy‑paste friendly examples that demonstrate common and advanced use cases for working with Icelandic kennitala using this library.

## Prerequisites

- Python 3.9+
- Recommended: create a virtual environment and install the package in editable mode

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

## Run the examples

- Run the comprehensive usage tour:

```bash
python examples/usage_examples.py
```

- Run the XML loader example (parses the included sample dataset and validates records):

```bash
python examples/loader_example.py
```

## What’s covered

- Normalization and formatting
- Strict vs relaxed validation (checksum policy)
- Parsing to structured data (`ParsedKennitala`)
- Masking for safe display/logging
- Entity detection (individual vs company)
- Synthetic dataset marker detection (14/15 in sequence)
- Generating IDs for testing (personal/company; by date; random ranges)
- Extracting birth/registration date
- Loading and validating sample XML records

Each example section in `usage_examples.py` includes a short explanation and prints concrete inputs/outputs so you can see exactly what each function does and how to integrate it.
