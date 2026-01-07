"""
Comprehensive usage examples for the ice_ken library.

Each section below focuses on a practical use case and prints inputs
and outputs so you can copy, paste, and adapt for your own code.

Recommended to run from repo root after installing in editable mode:

    python examples/usage_examples.py
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Iterable

from ice_ken import (
    normalize,
    format_kennitala,
    is_valid,
    parse,
    mask,
    is_company,
    is_personal,
    is_dataset_id,
    ParsedKennitala,
)
from ice_ken.kennitala import (
    generate_personal,
    generate_company,
    generate_personal_for_date,
    generate_company_for_date,
    random_personal,
    random_company,
    get_birth_date,
)


def print_section(title: str) -> None:
    print("\n" + "=" * len(title))
    print(title)
    print("=" * len(title))


def demo_normalize_and_format() -> None:
    """Clean user input and format consistently as DDMMYY-NNNX."""
    print_section("Normalize and format")
    raw = "120174 3399"  # spaces or other separators are common in user input
    digits = normalize(raw)
    print(f"Input: {raw}")
    print(f"Digits only: {digits}")
    try:
        formatted = format_kennitala(digits)
        print(f"Formatted: {formatted}")
    except ValueError as e:
        print(f"Format error: {e}")


def demo_validation_strict_vs_relaxed(sample: str) -> None:
    """Validate in strict policy (checksum) vs relaxed (ignores checksum)."""
    print_section("Validation: strict vs relaxed policy")
    print(f"Sample: {sample}")
    print(f"Digits: {normalize(sample)}")
    v_strict = is_valid(sample, enforce_checksum=True)
    v_relaxed = is_valid(sample, enforce_checksum=False)
    print(f"Strict valid (checksum enforced): {v_strict}")
    print(f"Relaxed valid (checksum ignored): {v_relaxed}")
    print("Tip: From 2026 policy changes, relaxed may be appropriate for new IDs.")


def demo_parse_to_struct(sample: str) -> None:
    """Parse a kennitala to structured data (birth date, entity, etc.)."""
    print_section("Parse to structured data")
    print(f"Input: {sample}")
    try:
        info: ParsedKennitala = parse(sample, enforce_checksum=False)
        print("Parsed:")
        print(f"  digits: {info.digits}")
        print(f"  formatted: {info.formatted}")
        print(f"  birth_date: {info.birth_date} (YYYY-MM-DD)")
        print(f"  century_indicator: {info.century_indicator}")
        print(f"  entity_type: {info.entity_type}")
    except ValueError as e:
        print(f"Parse error: {e}")


def demo_masking(sample: str) -> None:
    """Mask for safe display or logging while retaining last N digits."""
    print_section("Masking for safe display")
    print(f"Input: {sample}")
    print(f"Masked (default last 4 visible): {mask(sample)}")
    print(f"Masked (last 2 visible): {mask(sample, visible_tail=2)}")
    print(f"Masked (fully hidden): {mask(sample, visible_tail=0)}")


def demo_entity_detection(samples: Iterable[str]) -> None:
    """Differentiate individuals from companies using the day+40 rule."""
    print_section("Entity detection: individual vs company")
    for s in samples:
        kind = "company" if is_company(s) else ("individual" if is_personal(s) else "unknown")
        print(f"{format_kennitala(s)} -> {kind}")


def demo_dataset_marker(samples: Iterable[str]) -> None:
    """Identify synthetic IDs from the official dataset (14/15 in sequence)."""
    print_section("Synthetic dataset marker detection")
    for s in samples:
        print(f"{format_kennitala(s)} -> is_dataset_id={is_dataset_id(s)}")


def demo_generation() -> None:
    """Generate test IDs: personal/company, strict/relaxed, formatted/raw."""
    print_section("Generating test IDs")
    random.seed(42)
    p_strict = generate_personal(enforce_checksum=True, formatted=True)
    p_relaxed = generate_personal(enforce_checksum=False, formatted=False)
    c_strict = generate_company(enforce_checksum=True, formatted=True)
    c_relaxed = generate_company(enforce_checksum=False, formatted=False)
    print(f"Personal (strict, formatted): {p_strict}")
    print(f"Personal (relaxed, digits): {p_relaxed}")
    print(f"Company  (strict, formatted): {c_strict}")
    print(f"Company  (relaxed, digits): {c_relaxed}")
    print("Note: Relaxed IDs may intentionally fail checksum for negative testing.")


def demo_generation_for_specific_dates() -> None:
    """Generate IDs tied to specific dates (useful for fixtures)."""
    print_section("Generating for specific dates")
    random.seed(7)
    birth = date(1990, 5, 17)
    reg = date(2012, 11, 30)
    p = generate_personal_for_date(birth, enforce_checksum=True, formatted=True)
    c = generate_company_for_date(reg, enforce_checksum=True, formatted=True)
    print(f"Personal for {birth}: {p}")
    print(f"Company  for {reg}: {c}")


def demo_random_in_ranges() -> None:
    """Generate random IDs within a date range (inclusive)."""
    print_section("Random generation within ranges")
    random.seed(123)
    start = date(1985, 1, 1)
    end = date(1995, 12, 31)
    p = random_personal(start, end, enforce_checksum=True, formatted=True)
    print(f"Random personal between {start} and {end}: {p}")
    start_c = date(2005, 1, 1)
    end_c = date(2007, 12, 31)
    c = random_company(start_c, end_c, enforce_checksum=True, formatted=True)
    print(f"Random company  between {start_c} and {end_c}: {c}")


def demo_get_birth_date(sample: str) -> None:
    """Extract just the resolved birth/registration date."""
    print_section("Get birth/registration date")
    try:
        d = get_birth_date(sample, enforce_checksum=False)
        print(f"{format_kennitala(sample)} -> {d}")
    except ValueError as e:
        print(f"Error: {e}")


def demo_bulk_validation(samples: Iterable[str]) -> None:
    """Validate a batch of inputs like a simple ingestion pipeline."""
    print_section("Bulk validation pipeline example")
    valid_relaxed = []
    invalid = []
    for s in samples:
        if is_valid(s, enforce_checksum=False):
            valid_relaxed.append(format_kennitala(s))
        else:
            invalid.append(normalize(s))
    print(f"Valid (relaxed policy): {valid_relaxed}")
    print(f"Invalid: {invalid}")


def main() -> None:
    # Use deterministic seeds so printed examples are repeatable
    random.seed(2026)

    # Prepare a couple of concrete IDs for demonstrations
    # We generate them to avoid shipping real personal data.
    ref_birth = date(1984, 1, 12)
    ref_reg = date(2014, 3, 9)
    kt_personal = generate_personal_for_date(ref_birth, enforce_checksum=True, formatted=True)
    kt_company = generate_company_for_date(ref_reg, enforce_checksum=True, formatted=True)

    # 1) normalize and format
    demo_normalize_and_format()

    # 2) validation, strict vs relaxed
    # Craft an ID that is structurally valid but likely bad checksum by toggling checksum digit
    digits = normalize(kt_personal)
    bad_checksum = digits[:-2] + ("9" if digits[-2] != "9" else "8") + digits[-1]
    demo_validation_strict_vs_relaxed(bad_checksum)

    # 3) parse to structured data
    demo_parse_to_struct(kt_personal)
    demo_parse_to_struct(kt_company)

    # 4) masking
    demo_masking(kt_personal)

    # 5) entity detection
    demo_entity_detection([kt_personal, kt_company])

    # 6) dataset marker detection
    # Construct samples with the synthetic dataset markers in sequence (digits 7–8)
    # by taking any valid first 6 and last 2 digits and injecting sequence "14" and "15".
    ktd = normalize(kt_personal)
    ds_14 = ktd[:6] + "14" + ktd[8:]
    ds_15 = ktd[:6] + "15" + ktd[8:]
    demo_dataset_marker([ds_14, ds_15, ktd])

    # 7) generation utilities
    demo_generation()
    demo_generation_for_specific_dates()
    demo_random_in_ranges()

    # 8) get birth date helper
    demo_get_birth_date(kt_personal)

    # 9) bulk validation pipeline
    sample_batch = [kt_personal, kt_company, "120174-3399", "000000-0000"]
    demo_bulk_validation(sample_batch)


if __name__ == "__main__":
    main()
