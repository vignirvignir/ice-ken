# Kennitala (Icelandic National ID) — Overview

This document explains how Icelandic national ID numbers (kennitala) are structured and calculated, and highlights important considerations for software systems that process them.

## Policy Notice (February 18, 2026)

Starting February 18, 2026, Registers Iceland will issue kennitalas (both regular kennitala and system IDs, kerfiskennitala) without a computed Modulus 11 check digit. As a result, these IDs may not satisfy the traditional check-digit test. Systems that perform strict check-digit validation must be reviewed and updated to accommodate this change.

Key points:

- Scope: Applies to individuals registered in the National Register and to System Identification Numbers (kerfiskennitala).
- Rationale and impact: Removing the check digit significantly increases the available ID space and avoids allocation bottlenecks.
- Consequence: From the effective date onward, newly issued IDs can contain any value in the 9th digit; they should not be rejected solely because they fail the Modulus 11 parity test.

### Synthetic IDs for Testing

Registers Iceland provides synthetic kennitalas (three for children, three for adults) that intentionally fail the check-digit test so organisations can verify that their systems accept IDs without a valid parity digit.

Recommended test procedure:

1. Use two test kennitalas that fail the check-digit test:
   - One that exists in the National Register.
   - One that does not exist in the National Register.
2. Interpret outcomes:
   - If neither works: the system (or a subsystem) is still enforcing the check-digit test.
   - If only the National Register ID works: the system verifies against the register and does not use the check-digit test.
   - If both work: the system is not using either the National Register or the check-digit test for validation.

Note: Acquire synthetic test IDs from Registers Iceland using the official channel provided to organisations.

#### Official Synthetic Dataset (Gervigögn)

Registers Iceland also maintains a broader synthetic dataset ("Þjóðskrá – gervigögn") for development and testing of integrations. This dataset:

- Contains no real data from the National Register and is intended solely for testing.
- Uses a visual marker in names: test person and company names include the uppercase letters "ÞÍ" to indicate synthetic data.
- Distinguishes synthetic kennitalas from real ones by placing the sequence "14" or "15" in the sequence positions (digits 7–8) of each kennitala.
- Provides kennitalas that are randomly generated and not associated with any real individual or entity in the National Register.
- Comes with a disclaimer that Registers Iceland does not accept responsibility for how the synthetic data is used.

Implementation tip: If you need to detect dataset kennitalas during test runs, you can check whether the two sequence digits (positions 7–8 in `DDMMYY-NNNX`, i.e., indices 6–7 of the digits-only form) are either `"14"` or `"15"`. The `ice_ken` package provides `is_dataset_id(value)` for this convenience. Do not rely on this condition in production; it is only a convention used within the official synthetic dataset.

## Allocation

Kennitala is assigned automatically when an individual is registered in official systems (e.g., at birth registration for a newborn in Iceland, or upon first registration for others). The ID encodes the date of birth and includes sequencing and integrity digits.

## Structure

Kennitala consists of 10 digits and is commonly written as `DDMMYY-NNNX`:

- Digits 1–2: Day of month (`DD`)
- Digits 3–4: Month (`MM`)
- Digits 5–6: Year (two digits, `YY`)
- Digits 7–8: Sequence digits (assigned in order; often starting from 20)
- Digit 9: Check digit (Modulus 11)
- Digit 10: Century indicator — `8` for 1800s, `9` for 1900s, `0` for 2000s

Individuals use a real calendar day (`01`–`31`). Companies and other legal entities are distinguished by adding `40` to the day field, yielding `DD = 41–71` (so the first digit is `4–7`). When validating dates for companies, subtract `40` from the `DD` value to resolve the actual day.

Example (birth date 12 January 1960): the first six digits are `120160`.

## Century Indicator

The 10th digit encodes the century of birth:

- `8` → 1800–1899
- `9` → 1900–1999
- `0` → 2000–2099

## Check Digit (Modulus 11)

Historically, the check digit (9th digit) is used to reduce transcription errors. It is computed using a Modulus 11 algorithm applied to the first eight digits (day, month, year, and the two sequence digits) with the weight vector `[3, 2, 7, 6, 5, 4, 3, 2]`:

1. Multiply each of the first eight digits by the corresponding weight.
2. Sum the products and compute `remainder = sum % 11`.
3. Compute `check = 11 - remainder`.
   - If `check == 11`, the check digit is `0`.
   - If `check == 10`, the digit is unusable; increment the sequence and recompute.
4. The resulting check digit becomes the 9th digit of the kennitala.

### Worked Example

For `120160` and a sequence of `33`, the eight digits used in the calculation are:

```
digits: 1 2 0 1 6 0 3 3
weights:3 2 7 6 5 4 3 2
products:3 4 0 6 30 0 9 6
sum = 58 → remainder = 58 % 11 = 3 → check = 11 - 3 = 8
```

Thus, the check digit is `8`. With a century indicator of `9` (1900s), the full kennitala is `120160-3389`.

From February 18, 2026, newly issued kennitalas may have a 9th digit that does not conform to this algorithm. Systems should be prepared to accept IDs that fail the Modulus 11 check where policy requires.

## Implementation Considerations

- Do not assume that all kennitalas pass the Modulus 11 test after February 18, 2026.
- Validation should consider structural checks (length, digits, date) and century indicator. Apply the check-digit rule only when required by business policy.
- Provide configurable validation modes:
  - Strict mode: enforce Modulus 11 parity (legacy behaviour; fails for non-conforming IDs).
  - Relaxed mode: skip Modulus 11 parity while still enforcing structure and date validity.
- When integrating with the National Register, treat parity failures as non-fatal where mandated, and rely on registry presence/absence checks for identity confirmation.

## Validation Modes (ice-ken)

The `ice_ken` package supports both strict and relaxed validation to accommodate the 2026 policy change:

- Strict: `is_valid(value)` — validates structure, date, and the Modulus 11 check digit (9th digit).
- Relaxed: `is_valid(value, enforce_checksum=False)` — validates structure and date only; checksum is not enforced.

Example:

```
from ice_ken import is_valid

valid_strict = is_valid("120160-3389")                # True (passes checksum)
valid_relaxed = is_valid("120160-3379", enforce_checksum=False)  # True (ignores checksum)
valid_strict_again = is_valid("120160-3379")          # False (fails checksum)
```

Tip: In workflows that require confirmation against the National Register, prefer relaxed validation locally and rely on the registry check for final verification.

## Digit Roles Summary

| Field | Individuals (person)            | Companies/legal entities        | Notes                                           |
| ----: | ------------------------------- | ------------------------------- | ----------------------------------------------- |
|  D1D2 | `01–31` (calendar day)          | `41–71` (day + 40)              | Subtract 40 to resolve actual day for companies |
|  M1M2 | `01–12` (month)                 | `01–12` (month)                 | —                                               |
|  Y1Y2 | `00–99` (year)                  | `00–99` (year)                  | Two-digit year                                  |
|  R1R2 | `20–99` (typical)               | `20–99` (typical)               | Allocation/sequence digits                      |
|     P | 9th digit: check digit (Mod 11) | 9th digit: check digit (Mod 11) | From 2026, may not be enforced for new IDs      |
|     C | 10th digit: century indicator   | 10th digit: century indicator   | `8`=1800s, `9`=1900s, `0`=2000s                 |

Notation: `DDMMYY-RRPC` is commonly written with a hyphen after the first six digits.

## API Cheatsheet (ice-ken)

```python
from ice_ken import (
 normalize, format_kennitala,
 is_valid, parse,
 is_company, is_personal,
 mask,
 generate_personal, generate_company,
)

raw = "120160-3389"

# Normalize and format
digits = normalize(raw)               # "1201603389"
formatted = format_kennitala(digits)  # "120160-3389"

# Validation (strict vs relaxed)
is_valid(raw)                         # True (strict: checksum enforced)
is_valid(raw, enforce_checksum=False) # True (relaxed: checksum ignored)

# Entity type helpers
is_personal(raw)                      # True
is_company("520160-3379")            # True (company: day=52 → 12)

# Parsing (returns ParsedKennitala)
info = parse(raw)                     # strict parse
info_relaxed = parse("520160-3379", enforce_checksum=False)
info_relaxed.birth_date               # datetime.date(1960, 1, 12)
info_relaxed.entity_type              # "company"

# Masking for safe display/logging
mask(raw)                             # "******-3389" (default tail=4)

# Generating test IDs
kt_person = generate_personal()                     # Strict checksum
kt_person_relaxed = generate_personal(False)        # Relaxed
kt_company = generate_company()                     # Strict
kt_company_relaxed = generate_company(False)        # Relaxed
```
