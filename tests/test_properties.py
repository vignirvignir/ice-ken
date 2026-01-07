from datetime import date, timedelta
import random
from typing import Optional

from ice_ken import (
    is_valid,
    parse,
    is_company,
    is_personal,
    format_kennitala,
)


def _compute_checksum(first8: str) -> Optional[int]:
    weights = [3, 2, 7, 6, 5, 4, 3, 2]
    total = sum(int(d) * w for d, w in zip(first8, weights))
    remainder = total % 11
    check = 11 - remainder
    if check == 11:
        return 0
    if check == 10:
        return None
    return check


def _century_indicator(year: int) -> int:
    if 1800 <= year <= 1899:
        return 8
    if 1900 <= year <= 1999:
        return 9
    if 2000 <= year <= 2099:
        return 0
    raise AssertionError("year out of range")


def test_fuzz_personal_strict_valid_parses_and_flags():
    random.seed(1234)
    start = date(1930, 1, 1)
    end = date(2025, 12, 31)
    span = (end - start).days
    cases = 0
    while cases < 200:
        dt = start + timedelta(days=random.randint(0, span))
        dd, mm, yy = dt.day, dt.month, dt.year % 100
        c = _century_indicator(dt.year)
        r = random.randint(20, 99)
        first8 = f"{dd:02d}{mm:02d}{yy:02d}{r:02d}"
        p = _compute_checksum(first8)
        if p is None:
            continue
        digits = f"{first8}{p}{c}"
        assert is_valid(digits)
        assert is_personal(digits)
        info = parse(digits)
        assert info.birth_date == dt
        assert info.entity_type == "individual"
        # Round-trip formatting preserves structure
        assert format_kennitala(digits).replace("-", "") == digits
        cases += 1


def test_fuzz_company_strict_valid_parses_and_flags():
    random.seed(5678)
    start = date(1990, 1, 1)
    end = date(2025, 12, 31)
    span = (end - start).days
    cases = 0
    while cases < 200:
        dt = start + timedelta(days=random.randint(0, span))
        dd, mm, yy = dt.day + 40, dt.month, dt.year % 100
        c = _century_indicator(dt.year)
        r = random.randint(20, 99)
        first8 = f"{dd:02d}{mm:02d}{yy:02d}{r:02d}"
        p = _compute_checksum(first8)
        if p is None:
            continue
        digits = f"{first8}{p}{c}"
        assert is_valid(digits)
        assert is_company(digits)
        info = parse(digits)
        # Company day resolves by subtracting 40
        assert (
            info.birth_date.year == dt.year
            and info.birth_date.month == dt.month
            and info.birth_date.day == dt.day
        )
        assert info.entity_type == "company"
        cases += 1


def test_fuzz_relaxed_vs_strict_divergence():
    random.seed(91011)
    # Create a mixture of personal and company forms, perturb checksum
    count = 0
    while count < 200:
        is_comp = random.choice([False, True])
        year = random.randint(1930, 2025) if not is_comp else random.randint(1990, 2025)
        month = random.randint(1, 12)
        # Pick a valid day for month (simple approach: try days until date ok)
        for _ in range(10):
            day = random.randint(1, 28)  # keep simple to avoid month-length logic
            try:
                base = date(year, month, day)
                break
            except ValueError:
                continue
        else:
            continue
        dd = base.day + (40 if is_comp else 0)
        mm = base.month
        yy = base.year % 100
        c = _century_indicator(base.year)
        r = random.randint(20, 99)
        first8 = f"{dd:02d}{mm:02d}{yy:02d}{r:02d}"
        p = _compute_checksum(first8)
        # Force a wrong parity if possible
        wrong_p = random.choice(
            [d for d in range(10) if d != (p if p is not None else -1)]
        )
        digits = f"{first8}{wrong_p}{c}"
        assert is_valid(digits, enforce_checksum=False) is True
        assert is_valid(digits, enforce_checksum=True) is False
        count += 1
