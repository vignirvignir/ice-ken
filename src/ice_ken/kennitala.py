from __future__ import annotations

"""
Kennitala helpers for Icelandic national ID numbers.

A kennitala consists of 10 digits, typically formatted as "DDMMYY-NNNX":
- Digits 1-6: day, month, year (two digits)
- Digits 7-8: sequence numbers
- Digit 9: check digit (Modulus 11; policy exception from 2026)
- Digit 10: century indicator (8=1800s, 9=1900s, 0=2000s)

Individuals use a real calendar day (01–31). Companies and other legal
entities are distinguished by adding 40 to the day field, resulting in
`DD` = 41–71 (so the first digit is 4–7). When resolving a calendar date
for validation, subtract 40 from the day for company IDs.

This module provides:
- normalize: strip separators and whitespace, keep digits only
- format_kennitala: format digits as DDMMYY-NNNX
- is_valid: structural + date validation with optional checksum enforcement
- parse: return structured information including resolved birth date
- mask: hide sensitive digits for safe display/logging
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional
import random


@dataclass(frozen=True)
class ParsedKennitala:
    digits: str
    formatted: str
    birth_date: date
    century_indicator: int
    entity_type: str  # "individual" | "company"


def normalize(value: str) -> str:
    """Return only the digits of a kennitala.

    Parameters:
        value: String possibly containing separators like '-' or spaces.

    Returns:
        Digits-only string.
    """
    return "".join(ch for ch in value if ch.isdigit())


def format_kennitala(value: str) -> str:
    """Format a kennitala as DDMMYY-NNNX.

    Accepts either a digits-only string or a string with separators.
    """
    digits = normalize(value)
    if len(digits) != 10:
        raise ValueError("Kennitala must contain exactly 10 digits to format")
    return f"{digits[0:6]}-{digits[6:10]}"


def _century_base(indicator: int) -> Optional[int]:
    if indicator == 8:
        return 1800
    if indicator == 9:
        return 1900
    if indicator == 0:
        return 2000
    return None


def _resolve_birth_date(digits: str) -> Optional[date]:
    # digits: 10-digit kennitala (digits only)
    day_raw = int(digits[0:2])
    # Company IDs have day offset +40
    if 41 <= day_raw <= 71:
        day = day_raw - 40
    else:
        day = day_raw
    month = int(digits[2:4])
    year_two = int(digits[4:6])
    century = _century_base(int(digits[9]))
    if century is None:
        return None
    full_year = century + year_two
    try:
        return date(full_year, month, day)
    except ValueError:
        return None


def _is_company_digits(digits: str) -> bool:
    if len(digits) != 10 or not digits.isdigit():
        return False
    dd = int(digits[0:2])
    return 41 <= dd <= 71


def _checksum_ok(digits: str) -> bool:
    # Checksum uses the first 8 digits and weights [3,2,7,6,5,4,3,2]
    weights = [3, 2, 7, 6, 5, 4, 3, 2]
    total = sum(int(d) * w for d, w in zip(digits[:8], weights))
    remainder = total % 11
    check = 11 - remainder
    if check == 11:
        check = 0
    if check == 10:
        # 10 indicates invalid kennitala
        return False
    return check == int(digits[8])


def _compute_checksum_for_first8(first8: str) -> Optional[int]:
    """Compute Mod 11 checksum digit for the first 8 digits.

    Returns an int 0-9, or None if the result is 10 (invalid by definition).
    """
    weights = [3, 2, 7, 6, 5, 4, 3, 2]
    total = sum(int(d) * w for d, w in zip(first8, weights))
    remainder = total % 11
    check = 11 - remainder
    if check == 11:
        return 0
    if check == 10:
        return None
    return check


def is_valid(value: str, enforce_checksum: bool = True) -> bool:
    """Return True if the kennitala is valid under the selected policy.

    Always validates:
    - length and digit-only normalization
    - century indicator (8/9/0)
    - calendar date resolution

    Additionally validates checksum (mod 11) iff ``enforce_checksum`` is True.
    From Feb 18, 2026, newly issued IDs may not satisfy the checksum.
    """
    digits = normalize(value)
    if len(digits) != 10:
        return False
    # Valid century indicator (10th digit)
    if _century_base(int(digits[9])) is None:
        return False
    # Valid birth/registration date (handles company day offset)
    if _resolve_birth_date(digits) is None:
        return False
    # Checksum (conditionally enforced)
    return _checksum_ok(digits) if enforce_checksum else True


def parse(value: str, enforce_checksum: bool = True) -> ParsedKennitala:
    """Parse a kennitala into structured information.

    Raises ValueError if the kennitala is not valid.
    """
    digits = normalize(value)
    if len(digits) != 10:
        raise ValueError("Kennitala must contain exactly 10 digits")
    birth = _resolve_birth_date(digits)
    if birth is None:
        raise ValueError("Invalid kennitala date or century indicator")
    if enforce_checksum and not _checksum_ok(digits):
        raise ValueError("Invalid kennitala checksum")
    entity = "company" if _is_company_digits(digits) else "individual"
    return ParsedKennitala(
        digits=digits,
        formatted=format_kennitala(digits),
        birth_date=birth,
        century_indicator=int(digits[9]),
        entity_type=entity,
    )


def mask(value: str, visible_tail: int = 4) -> str:
    """Return a masked representation, exposing only the last `visible_tail` digits.

    Example: **** **-**1234
    """
    digits = normalize(value)
    if len(digits) != 10:
        raise ValueError("Kennitala must contain exactly 10 digits to mask")
    tail = digits[-visible_tail:] if visible_tail > 0 else ""
    masked_head = "*" * (10 - len(tail))
    masked = f"{masked_head[0:6]}-{masked_head[6:]}{tail}"
    return masked


def is_company(value: str) -> bool:
    """Return True if the kennitala belongs to a company/legal entity.

    Determination is based on the day field being 41–71 (day + 40 rule).
    """
    return _is_company_digits(normalize(value))


def is_personal(value: str) -> bool:
    """Return True if the kennitala belongs to an individual (not a company)."""
    digits = normalize(value)
    return len(digits) == 10 and digits.isdigit() and not _is_company_digits(digits)


def is_dataset_id(value: str) -> bool:
    """Return True if the kennitala matches the official synthetic dataset marker.

    The official "Þjóðskrá – gervigögn" dataset distinguishes synthetic IDs by
    placing "14" or "15" in the sequence positions (digits 7–8 of the 10-digit
    form, i.e., positions 6–7 zero-indexed). This helper checks for that
    convention. It does not validate the checksum or date and should be used
    only in test contexts, not for production logic.
    """
    digits = normalize(value)
    if len(digits) != 10 or not digits.isdigit():
        return False
    return digits[6:8] in ("14", "15")


def _random_date(start: date, end: date) -> date:
    """Return a random date between start and end (inclusive)."""
    start_ordinal = start.toordinal()
    end_ordinal = end.toordinal()
    return date.fromordinal(random.randint(start_ordinal, end_ordinal))


def _century_indicator_for_year(year: int) -> int:
    if 1800 <= year <= 1899:
        return 8
    if 1900 <= year <= 1999:
        return 9
    if 2000 <= year <= 2099:
        return 0
    raise ValueError("Year out of supported range for kennitala")


def generate_personal(enforce_checksum: bool = True, formatted: bool = True) -> str:
    """Generate a random personal kennitala.

    - If enforce_checksum is True, returns a checksum-valid ID.
    - If False, returns a structurally valid ID that may fail the checksum.
    - If formatted is True (default), returns "DDMMYY-NNNX"; otherwise returns 10 digits.
    """
    # Pick a reasonable year range for individuals
    birth = _random_date(date(1930, 1, 1), date(2025, 12, 31))
    dd = birth.day
    mm = birth.month
    yy = birth.year % 100
    c = _century_indicator_for_year(birth.year)

    # Sequence 20-99; iterate until checksum is acceptable (if needed)
    while True:
        r = random.randint(20, 99)
        first8 = f"{dd:02d}{mm:02d}{yy:02d}{r:02d}"
        if enforce_checksum:
            chk = _compute_checksum_for_first8(first8)
            if chk is None:
                continue  # try a different sequence
            p = chk
        else:
            # Intentionally avoid correct checksum when possible
            chk = _compute_checksum_for_first8(first8)
            if chk is None:
                p = random.randint(0, 9)
            else:
                choices = [d for d in range(10) if d != chk]
                p = random.choice(choices)
        digits = f"{first8}{p}{c}"
        break

    return format_kennitala(digits) if formatted else digits


def generate_company(enforce_checksum: bool = True, formatted: bool = True) -> str:
    """Generate a random company/legal-entity kennitala.

    - Company day uses +40 encoding (DD = 41–71).
    - If enforce_checksum is True, returns a checksum-valid ID.
    - If False, returns a structurally valid ID that may fail the checksum.
    - If formatted is True (default), returns "DDMMYY-NNNX"; otherwise returns 10 digits.
    """
    # Registration date range for companies (arbitrary but reasonable)
    reg = _random_date(date(1990, 1, 1), date(2025, 12, 31))
    dd = reg.day + 40  # encode as company
    mm = reg.month
    yy = reg.year % 100
    c = _century_indicator_for_year(reg.year)

    while True:
        r = random.randint(20, 99)
        first8 = f"{dd:02d}{mm:02d}{yy:02d}{r:02d}"
        if enforce_checksum:
            chk = _compute_checksum_for_first8(first8)
            if chk is None:
                continue
            p = chk
        else:
            chk = _compute_checksum_for_first8(first8)
            if chk is None:
                p = random.randint(0, 9)
            else:
                choices = [d for d in range(10) if d != chk]
                p = random.choice(choices)
        digits = f"{first8}{p}{c}"
        break

    return format_kennitala(digits) if formatted else digits


def generate_personal_for_date(
    birth_date: date, *, enforce_checksum: bool = True, formatted: bool = True
) -> str:
    """Generate a personal kennitala for a specific birth date.

    - If enforce_checksum is True, returns a checksum-valid ID.
    - If False, returns a structurally valid ID that may fail the checksum.
    - If formatted is True (default), returns "DDMMYY-NNNX"; otherwise returns 10 digits.
    """
    dd = birth_date.day
    mm = birth_date.month
    yy = birth_date.year % 100
    c = _century_indicator_for_year(birth_date.year)

    while True:
        r = random.randint(20, 99)
        first8 = f"{dd:02d}{mm:02d}{yy:02d}{r:02d}"
        if enforce_checksum:
            chk = _compute_checksum_for_first8(first8)
            if chk is None:
                continue
            p = chk
        else:
            chk = _compute_checksum_for_first8(first8)
            if chk is None:
                p = random.randint(0, 9)
            else:
                choices = [d for d in range(10) if d != chk]
                p = random.choice(choices)
        digits = f"{first8}{p}{c}"
        break

    return format_kennitala(digits) if formatted else digits


def generate_company_for_date(
    reg_date: date, *, enforce_checksum: bool = True, formatted: bool = True
) -> str:
    """Generate a company/legal-entity kennitala for a specific registration date.

    - Company day uses +40 encoding (DD = 41–71).
    - If enforce_checksum is True, returns a checksum-valid ID.
    - If False, returns a structurally valid ID that may fail the checksum.
    - If formatted is True (default), returns "DDMMYY-NNNX"; otherwise returns 10 digits.
    """
    dd = reg_date.day + 40
    mm = reg_date.month
    yy = reg_date.year % 100
    c = _century_indicator_for_year(reg_date.year)

    while True:
        r = random.randint(20, 99)
        first8 = f"{dd:02d}{mm:02d}{yy:02d}{r:02d}"
        if enforce_checksum:
            chk = _compute_checksum_for_first8(first8)
            if chk is None:
                continue
            p = chk
        else:
            chk = _compute_checksum_for_first8(first8)
            if chk is None:
                p = random.randint(0, 9)
            else:
                choices = [d for d in range(10) if d != chk]
                p = random.choice(choices)
        digits = f"{first8}{p}{c}"
        break

    return format_kennitala(digits) if formatted else digits


def random_personal(
    start: date,
    end: date,
    *,
    enforce_checksum: bool = True,
    formatted: bool = True,
) -> str:
    """Generate a random personal kennitala within a given date range (inclusive).

    Raises ValueError if start > end.
    """
    if start > end:
        raise ValueError("Start must not be > end")
    birth = _random_date(start, end)
    return generate_personal_for_date(birth, enforce_checksum=enforce_checksum, formatted=formatted)


def random_company(
    start: date,
    end: date,
    *,
    enforce_checksum: bool = True,
    formatted: bool = True,
) -> str:
    """Generate a random company/legal-entity kennitala within a date range (inclusive).

    Raises ValueError if start > end.
    """
    if start > end:
        raise ValueError("Start must not be > end")
    reg = _random_date(start, end)
    return generate_company_for_date(reg, enforce_checksum=enforce_checksum, formatted=formatted)


def get_birth_date(value: str, *, enforce_checksum: bool = True) -> date:
    """Return the resolved birth/registration date for a kennitala.

    Wraps `parse()` and returns `ParsedKennitala.birth_date`.
    Raises ValueError if invalid under the selected policy.
    """
    return parse(value, enforce_checksum=enforce_checksum).birth_date
