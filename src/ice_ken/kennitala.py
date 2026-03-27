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
from typing import Literal
import random

__all__ = [
    "ParsedKennitala",
    "normalize",
    "format_kennitala",
    "is_valid",
    "parse",
    "mask",
    "is_company",
    "is_personal",
    "is_dataset_id",
    "generate_personal",
    "generate_company",
    "generate_kennitala",
    "generate_batch",
    "generate_personal_for_date",
    "generate_company_for_date",
    "random_personal",
    "random_company",
    "get_birth_date",
]


@dataclass(frozen=True, repr=False)
class ParsedKennitala:
    """Structured representation of a parsed kennitala.

    The default ``repr`` masks the ``digits`` and ``formatted`` fields to
    prevent accidental PII leakage in logs and tracebacks.
    """

    digits: str
    formatted: str
    birth_date: date
    century_indicator: int
    entity_type: str  # "individual" | "company"

    def __repr__(self) -> str:
        masked = mask(self.formatted)
        return (
            f"ParsedKennitala(formatted={masked!r}, "
            f"birth_date={self.birth_date!r}, "
            f"entity_type={self.entity_type!r})"
        )


def normalize(value: str) -> str:
    """Return only the digits of a kennitala.

    Parameters:
        value: String possibly containing separators like '-' or spaces.

    Returns:
        Digits-only string.

    Raises:
        TypeError: If ``value`` is not a string.
    """
    if not isinstance(value, str):
        raise TypeError(f"Expected str, got {type(value).__name__}")
    return "".join(ch for ch in value if "0" <= ch <= "9")


def format_kennitala(value: str) -> str:
    """Format a kennitala as DDMMYY-NNNX.

    Accepts either a digits-only string or a string with separators.
    """
    digits = normalize(value)
    if len(digits) != 10:
        raise ValueError("Kennitala must contain exactly 10 digits to format")
    return f"{digits[0:6]}-{digits[6:10]}"


def _century_base(indicator: int) -> int | None:
    if indicator == 8:
        return 1800
    if indicator == 9:
        return 1900
    if indicator == 0:
        return 2000
    return None


def _resolve_birth_date(digits: str) -> date | None:
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


def _compute_checksum_for_first8(first8: str) -> int | None:
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


def is_valid(value: str, enforce_checksum: bool = False) -> bool:
    """Return True if the kennitala is valid under the selected policy.

    Always validates:
    - length and digit-only normalization
    - century indicator (8/9/0)
    - calendar date resolution

    Additionally validates checksum (mod 11) iff ``enforce_checksum`` is True.

    .. note::

        Since Feb 18, 2026, Registers Iceland may issue kennitalas without
        valid Modulus 11 checksums. The default ``enforce_checksum=False``
        accepts these IDs. Pass ``enforce_checksum=True`` if you need to
        verify the checksum for IDs known to predate the policy change.

    .. versionchanged:: 2.0.0
        Default changed from ``True`` to ``False`` to avoid false negatives
        on newly issued kennitalas.
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


def parse(value: str, enforce_checksum: bool = False) -> ParsedKennitala:
    """Parse a kennitala into structured information.

    Raises ValueError if the kennitala is not valid.

    .. versionchanged:: 2.0.0
        Default changed from ``True`` to ``False`` to avoid rejecting
        newly issued kennitalas without valid checksums.
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

    Example: mask("1201603389") → "******-3389"

    Parameters:
        value: A kennitala string (with or without separator).
        visible_tail: Number of trailing digits to leave visible (0–10).

    Raises:
        ValueError: If the kennitala doesn't have 10 digits or visible_tail
            is out of range.
    """
    digits = normalize(value)
    if len(digits) != 10:
        raise ValueError("Kennitala must contain exactly 10 digits to mask")
    if not 0 <= visible_tail <= 10:
        raise ValueError("visible_tail must be between 0 and 10")
    if visible_tail == 10:
        return format_kennitala(digits)
    tail = digits[-visible_tail:] if visible_tail > 0 else ""
    masked_head = "*" * (10 - len(tail))
    masked = f"{masked_head[0:6]}-{masked_head[6:]}{tail}"
    return masked


def is_company(value: str) -> bool:
    """Return True if the kennitala belongs to a company/legal entity.

    Checks the day field (41–71) and validates the date and century indicator.
    Does not enforce the checksum.
    """
    digits = normalize(value)
    return _is_company_digits(digits) and is_valid(digits, enforce_checksum=False)


def is_personal(value: str) -> bool:
    """Return True if the kennitala belongs to an individual (not a company).

    Validates the date and century indicator. Does not enforce the checksum.
    """
    digits = normalize(value)
    if len(digits) != 10 or not digits.isdigit():
        return False
    return not _is_company_digits(digits) and is_valid(digits, enforce_checksum=False)


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


def _build_kennitala(
    target_date: date,
    *,
    company: bool,
    enforce_checksum: bool,
    formatted: bool,
) -> str:
    """Core generation logic shared by all public generators.

    Builds a 10-digit kennitala for the given date. For company IDs the day
    field is offset by +40. Retries with different sequence numbers until a
    valid checksum is found (when ``enforce_checksum`` is True) or deliberately
    avoids the correct checksum (when False).

    Uses Python's ``random`` module (Mersenne Twister), which is **not**
    cryptographically secure. Generated IDs are suitable for test fixtures
    and seed data, but must not be used as secrets or security tokens.
    """
    dd = target_date.day + (40 if company else 0)
    mm = target_date.month
    yy = target_date.year % 100
    c = _century_indicator_for_year(target_date.year)

    max_attempts = 1000
    for _ in range(max_attempts):
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
    else:
        raise RuntimeError(
            f"Failed to generate kennitala after {max_attempts} attempts"
        )

    return format_kennitala(digits) if formatted else digits


# Default date ranges for random generation
_PERSONAL_START = date(1930, 1, 1)
_COMPANY_START = date(1990, 1, 1)


def _default_end_date() -> date:
    """Return Dec 31 of the current year, capped at 2099 (century limit)."""
    return date(min(date.today().year, 2099), 12, 31)


def generate_personal(
    *,
    birth_date: date | None = None,
    enforce_checksum: bool = True,
    formatted: bool = True,
) -> str:
    """Generate a valid personal kennitala.

    Parameters:
        birth_date: Specific birth date to encode. If ``None``, a random date
            in the range 1930–2025 is used.
        enforce_checksum: When True (default), the returned ID passes Modulus 11
            validation. When False, the checksum digit is intentionally wrong.
        formatted: When True (default), returns ``"DDMMYY-NNNX"``; otherwise
            returns 10 bare digits.

    Returns:
        A kennitala string.

    Raises:
        ValueError: If ``birth_date`` has a year outside 1800–2099.
    """
    if birth_date is None:
        birth_date = _random_date(_PERSONAL_START, _default_end_date())
    return _build_kennitala(
        birth_date, company=False, enforce_checksum=enforce_checksum, formatted=formatted,
    )


def generate_company(
    *,
    reg_date: date | None = None,
    enforce_checksum: bool = True,
    formatted: bool = True,
) -> str:
    """Generate a valid company/legal-entity kennitala.

    Company IDs encode the day as ``actual_day + 40`` (DD = 41–71).

    Parameters:
        reg_date: Specific registration date to encode. If ``None``, a random
            date in the range 1990–2025 is used.
        enforce_checksum: When True (default), the returned ID passes Modulus 11
            validation. When False, the checksum digit is intentionally wrong.
        formatted: When True (default), returns ``"DDMMYY-NNNX"``; otherwise
            returns 10 bare digits.

    Returns:
        A kennitala string.

    Raises:
        ValueError: If ``reg_date`` has a year outside 1800–2099.
    """
    if reg_date is None:
        reg_date = _random_date(_COMPANY_START, _default_end_date())
    return _build_kennitala(
        reg_date, company=True, enforce_checksum=enforce_checksum, formatted=formatted,
    )


def generate_kennitala(
    kind: Literal["personal", "company"] = "personal",
    *,
    target_date: date | None = None,
    enforce_checksum: bool = True,
    formatted: bool = True,
    birth_date: date | None = None,
) -> str:
    """Generate a valid kennitala — unified entry point.

    Parameters:
        kind: ``"personal"`` (default) or ``"company"``.
        target_date: Date to encode (birth date for personal, registration date
            for company). If ``None``, a random date is chosen.
        enforce_checksum: When True (default), the returned ID passes Modulus 11.
        formatted: When True (default), returns ``"DDMMYY-NNNX"``.
        birth_date: Deprecated alias for ``target_date``.

    Returns:
        A kennitala string.

    Raises:
        ValueError: On invalid ``kind`` or unsupported year.
    """
    effective_date = target_date or birth_date
    if kind == "personal":
        return generate_personal(
            birth_date=effective_date, enforce_checksum=enforce_checksum, formatted=formatted,
        )
    if kind == "company":
        return generate_company(
            reg_date=effective_date, enforce_checksum=enforce_checksum, formatted=formatted,
        )
    raise ValueError(f"kind must be 'personal' or 'company', got {kind!r}")


def generate_batch(
    count: int,
    kind: Literal["personal", "company"] = "personal",
    *,
    target_date: date | None = None,
    enforce_checksum: bool = True,
    formatted: bool = True,
    birth_date: date | None = None,
) -> list[str]:
    """Generate multiple valid kennitölur.

    Parameters:
        count: Number of IDs to generate. Must be >= 0.
        kind: ``"personal"`` (default) or ``"company"``.
        target_date: If given, all IDs share this date; otherwise each gets a
            random date.
        enforce_checksum: When True (default), all IDs pass Modulus 11.
        formatted: When True (default), returns ``"DDMMYY-NNNX"`` strings.
        birth_date: Deprecated alias for ``target_date``.

    Returns:
        A list of kennitala strings. Duplicates are possible, especially
        when ``target_date`` is fixed — the sequence space is ~73 unique
        IDs per date with checksum enforcement.

    Raises:
        ValueError: On invalid ``count``, ``kind``, or unsupported year.
    """
    effective_date = target_date or birth_date
    if count < 0:
        raise ValueError("count must be >= 0")
    if count > 100_000:
        raise ValueError("count must be <= 100000")
    return [
        generate_kennitala(
            kind, target_date=effective_date, enforce_checksum=enforce_checksum, formatted=formatted,
        )
        for _ in range(count)
    ]


# --- Convenience aliases (backward compatibility) ---


def generate_personal_for_date(
    birth_date: date, *, enforce_checksum: bool = True, formatted: bool = True
) -> str:
    """Generate a personal kennitala for a specific birth date.

    Equivalent to ``generate_personal(birth_date, ...)``.
    """
    return generate_personal(birth_date=birth_date, enforce_checksum=enforce_checksum, formatted=formatted)


def generate_company_for_date(
    reg_date: date, *, enforce_checksum: bool = True, formatted: bool = True
) -> str:
    """Generate a company kennitala for a specific registration date.

    Equivalent to ``generate_company(reg_date=..., ...)``.
    """
    return generate_company(reg_date=reg_date, enforce_checksum=enforce_checksum, formatted=formatted)


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
    return generate_personal(birth_date=birth, enforce_checksum=enforce_checksum, formatted=formatted)


def random_company(
    start: date,
    end: date,
    *,
    enforce_checksum: bool = True,
    formatted: bool = True,
) -> str:
    """Generate a random company kennitala within a date range (inclusive).

    Raises ValueError if start > end.
    """
    if start > end:
        raise ValueError("Start must not be > end")
    reg = _random_date(start, end)
    return generate_company(reg_date=reg, enforce_checksum=enforce_checksum, formatted=formatted)


def get_birth_date(value: str, *, enforce_checksum: bool = False) -> date:
    """Return the resolved birth/registration date for a kennitala.

    Wraps `parse()` and returns `ParsedKennitala.birth_date`.
    Raises ValueError if invalid under the selected policy.
    """
    return parse(value, enforce_checksum=enforce_checksum).birth_date
