from datetime import date

import pytest

from ice_ken import (
    is_valid,
    is_company,
    is_personal,
    parse,
    format_kennitala,
    generate_personal,
    generate_company,
    generate_kennitala,
    generate_batch,
    generate_personal_for_date,
    generate_company_for_date,
    random_personal,
    random_company,
    get_birth_date,
)


# ---------------------------------------------------------------------------
# generate_personal
# ---------------------------------------------------------------------------


class TestGeneratePersonal:
    def test_random_strict_is_valid(self):
        for _ in range(20):
            kt = generate_personal()
            assert is_valid(kt)
            assert is_personal(kt)

    def test_random_relaxed_fails_strict(self):
        for _ in range(20):
            kt = generate_personal(enforce_checksum=False)
            assert is_valid(kt, enforce_checksum=False)
            assert is_personal(kt)
            assert is_valid(kt) is False

    def test_with_birth_date(self):
        d = date(1985, 7, 14)
        kt = generate_personal(birth_date=d, formatted=False)
        info = parse(kt)
        assert info.birth_date == d
        assert info.entity_type == "individual"
        assert info.century_indicator == 9

    def test_with_birth_date_2000s(self):
        d = date(2005, 3, 1)
        kt = generate_personal(birth_date=d, formatted=False)
        info = parse(kt)
        assert info.birth_date == d
        assert info.century_indicator == 0

    def test_with_birth_date_1800s(self):
        d = date(1850, 6, 15)
        kt = generate_personal(birth_date=d, formatted=False)
        info = parse(kt)
        assert info.birth_date == d
        assert info.century_indicator == 8

    def test_formatted_output(self):
        kt = generate_personal(formatted=True)
        assert len(kt) == 11
        assert kt[6] == "-"

    def test_unformatted_output(self):
        kt = generate_personal(formatted=False)
        assert len(kt) == 10
        assert "-" not in kt
        assert kt.isdigit()

    def test_leap_year_feb_29(self):
        d = date(2000, 2, 29)
        kt = generate_personal(birth_date=d, formatted=False)
        info = parse(kt)
        assert info.birth_date == d

    def test_year_boundary_dec_31(self):
        d = date(1999, 12, 31)
        kt = generate_personal(birth_date=d, formatted=False)
        info = parse(kt)
        assert info.birth_date == d

    def test_year_boundary_jan_1(self):
        d = date(2000, 1, 1)
        kt = generate_personal(birth_date=d, formatted=False)
        info = parse(kt)
        assert info.birth_date == d

    def test_unsupported_year_raises(self):
        with pytest.raises(ValueError, match="Year out of supported range"):
            generate_personal(birth_date=date(2100, 1, 1))

    def test_day_range(self):
        """Personal day field must be 01-31."""
        for _ in range(50):
            kt = generate_personal(formatted=False)
            dd = int(kt[:2])
            assert 1 <= dd <= 31


# ---------------------------------------------------------------------------
# generate_company
# ---------------------------------------------------------------------------


class TestGenerateCompany:
    def test_random_strict_is_valid(self):
        for _ in range(20):
            kt = generate_company()
            assert is_valid(kt)
            assert is_company(kt)

    def test_random_relaxed_fails_strict(self):
        for _ in range(20):
            kt = generate_company(enforce_checksum=False)
            assert is_valid(kt, enforce_checksum=False)
            assert is_company(kt)
            assert is_valid(kt) is False

    def test_with_reg_date(self):
        d = date(2012, 3, 5)
        kt = generate_company(reg_date=d, formatted=False)
        info = parse(kt)
        assert info.birth_date == d
        assert info.entity_type == "company"
        assert info.century_indicator == 0

    def test_formatted_output(self):
        kt = generate_company(formatted=True)
        assert len(kt) == 11
        assert kt[6] == "-"

    def test_unformatted_output(self):
        kt = generate_company(formatted=False)
        assert len(kt) == 10
        assert kt.isdigit()

    def test_company_day_offset(self):
        """Company day field must be 41-71 (actual day + 40)."""
        for _ in range(50):
            kt = generate_company(formatted=False)
            dd = int(kt[:2])
            assert 41 <= dd <= 71

    def test_unsupported_year_raises(self):
        with pytest.raises(ValueError, match="Year out of supported range"):
            generate_company(reg_date=date(1799, 6, 1))


# ---------------------------------------------------------------------------
# generate_kennitala (unified)
# ---------------------------------------------------------------------------


class TestGenerateKennitala:
    def test_personal_default(self):
        kt = generate_kennitala()
        assert is_personal(kt)
        assert is_valid(kt)

    def test_company(self):
        kt = generate_kennitala("company")
        assert is_company(kt)
        assert is_valid(kt)

    def test_personal_with_date(self):
        d = date(1990, 5, 20)
        kt = generate_kennitala("personal", birth_date=d, formatted=False)
        assert parse(kt).birth_date == d

    def test_company_with_date(self):
        d = date(2010, 11, 3)
        kt = generate_kennitala("company", birth_date=d, formatted=False)
        info = parse(kt)
        assert info.birth_date == d
        assert info.entity_type == "company"

    def test_personal_with_target_date(self):
        d = date(1990, 5, 20)
        kt = generate_kennitala("personal", target_date=d, formatted=False)
        assert parse(kt).birth_date == d

    def test_company_with_target_date(self):
        d = date(2010, 11, 3)
        kt = generate_kennitala("company", target_date=d, formatted=False)
        info = parse(kt)
        assert info.birth_date == d
        assert info.entity_type == "company"

    def test_invalid_kind_raises(self):
        with pytest.raises(ValueError, match="kind must be"):
            generate_kennitala("invalid")  # type: ignore[arg-type]

    def test_relaxed(self):
        kt = generate_kennitala(enforce_checksum=False)
        assert is_valid(kt, enforce_checksum=False)
        assert is_valid(kt) is False


# ---------------------------------------------------------------------------
# generate_batch
# ---------------------------------------------------------------------------


class TestGenerateBatch:
    def test_count_zero(self):
        assert generate_batch(0) == []

    def test_count_positive(self):
        batch = generate_batch(50)
        assert len(batch) == 50
        for kt in batch:
            assert is_valid(kt)
            assert is_personal(kt)

    def test_company_batch(self):
        batch = generate_batch(30, "company")
        assert len(batch) == 30
        for kt in batch:
            assert is_valid(kt)
            assert is_company(kt)

    def test_batch_with_date(self):
        d = date(1975, 8, 10)
        batch = generate_batch(10, birth_date=d, formatted=False)
        for kt in batch:
            assert parse(kt).birth_date == d

    def test_batch_with_target_date(self):
        d = date(1975, 8, 10)
        batch = generate_batch(10, target_date=d, formatted=False)
        for kt in batch:
            assert parse(kt).birth_date == d

    def test_negative_count_raises(self):
        with pytest.raises(ValueError, match="count must be >= 0"):
            generate_batch(-1)

    def test_all_unique_in_large_batch(self):
        """A large enough batch should produce mostly unique IDs."""
        batch = generate_batch(200, formatted=False)
        # With random sequences, collisions are possible but rare.
        # At minimum, more than half should be unique.
        assert len(set(batch)) > 100

    def test_batch_relaxed(self):
        batch = generate_batch(20, enforce_checksum=False)
        for kt in batch:
            assert is_valid(kt, enforce_checksum=False)
            assert is_valid(kt) is False


# ---------------------------------------------------------------------------
# Backward-compat aliases
# ---------------------------------------------------------------------------


class TestBackwardCompat:
    def test_generate_personal_for_date(self):
        d = date(1985, 7, 14)
        kt = generate_personal_for_date(d, enforce_checksum=True, formatted=False)
        info = parse(kt)
        assert info.entity_type == "individual"
        assert info.birth_date == d
        assert info.century_indicator == 9
        assert is_valid(kt)

    def test_generate_company_for_date(self):
        d = date(2012, 3, 5)
        kt = generate_company_for_date(d, enforce_checksum=True, formatted=False)
        info = parse(kt)
        assert info.entity_type == "company"
        assert info.birth_date == d

    def test_random_personal_in_range(self):
        start = date(1970, 1, 1)
        end = date(1970, 12, 31)
        kt = random_personal(start, end, enforce_checksum=False, formatted=False)
        info = parse(kt, enforce_checksum=False)
        assert info.entity_type == "individual"
        assert start <= info.birth_date <= end

    def test_random_company_in_range(self):
        start = date(2005, 6, 1)
        end = date(2005, 6, 30)
        kt = random_company(start, end, enforce_checksum=False, formatted=False)
        info = parse(kt, enforce_checksum=False)
        assert info.entity_type == "company"
        assert start <= info.birth_date <= end

    def test_get_birth_date(self):
        d = date(1999, 12, 31)
        kt = generate_personal(birth_date=d, formatted=False)
        assert get_birth_date(kt) == d

    def test_range_validation_errors(self):
        start = date(2020, 1, 2)
        end = date(2020, 1, 1)
        with pytest.raises(ValueError):
            random_personal(start, end)
        with pytest.raises(ValueError):
            random_company(start, end)


# ---------------------------------------------------------------------------
# Checksum behavior
# ---------------------------------------------------------------------------


class TestChecksumBehavior:
    def test_strict_generated_passes_checksum(self):
        """Every strict-generated ID must have a correct Mod 11 checksum."""
        for _ in range(100):
            kt = generate_personal(formatted=False)
            weights = [3, 2, 7, 6, 5, 4, 3, 2]
            total = sum(int(d) * w for d, w in zip(kt[:8], weights))
            remainder = total % 11
            expected = 0 if (11 - remainder) == 11 else 11 - remainder
            assert expected == int(kt[8])

    def test_relaxed_generated_has_wrong_checksum(self):
        """Relaxed-generated IDs should deliberately have the wrong checksum."""
        for _ in range(100):
            kt = generate_personal(enforce_checksum=False, formatted=False)
            weights = [3, 2, 7, 6, 5, 4, 3, 2]
            total = sum(int(d) * w for d, w in zip(kt[:8], weights))
            remainder = total % 11
            check = 11 - remainder
            if check == 11:
                check = 0
            if check == 10:
                continue  # can't verify this edge case
            assert int(kt[8]) != check


# ---------------------------------------------------------------------------
# Round-trip: generate → parse → validate
# ---------------------------------------------------------------------------


class TestRoundTrip:
    def test_personal_round_trip(self):
        for _ in range(50):
            kt = generate_personal(formatted=False)
            info = parse(kt)
            assert info.entity_type == "individual"
            assert is_valid(info.formatted)
            assert format_kennitala(kt).replace("-", "") == kt

    def test_company_round_trip(self):
        for _ in range(50):
            kt = generate_company(formatted=False)
            info = parse(kt)
            assert info.entity_type == "company"
            assert is_valid(info.formatted)

    def test_formatted_round_trip(self):
        kt_fmt = generate_personal(formatted=True)
        kt_digits = generate_personal(formatted=False)
        # Both should be parseable
        parse(kt_fmt)
        parse(kt_digits)


# ---------------------------------------------------------------------------
# Edge cases: dates
# ---------------------------------------------------------------------------


class TestDateEdgeCases:
    def test_all_months(self):
        """Generate a personal ID for each month of a year."""
        for month in range(1, 13):
            d = date(2000, month, 1)
            kt = generate_personal(birth_date=d, formatted=False)
            assert parse(kt).birth_date == d

    def test_day_31_months(self):
        """Months with 31 days should work fine."""
        for month in [1, 3, 5, 7, 8, 10, 12]:
            d = date(2000, month, 31)
            kt = generate_personal(birth_date=d, formatted=False)
            assert parse(kt).birth_date == d

    def test_feb_28_non_leap(self):
        d = date(2001, 2, 28)
        kt = generate_personal(birth_date=d, formatted=False)
        assert parse(kt).birth_date == d

    def test_feb_29_leap(self):
        d = date(2004, 2, 29)
        kt = generate_personal(birth_date=d, formatted=False)
        assert parse(kt).birth_date == d

    def test_century_boundaries(self):
        """Test generation at century boundaries."""
        for d, expected_ci in [
            (date(1899, 12, 31), 8),
            (date(1900, 1, 1), 9),
            (date(1999, 12, 31), 9),
            (date(2000, 1, 1), 0),
        ]:
            kt = generate_personal(birth_date=d, formatted=False)
            info = parse(kt)
            assert info.birth_date == d
            assert info.century_indicator == expected_ci

    def test_company_day_1_and_31(self):
        """Company day extremes: day 1 (DD=41) and day 31 (DD=71)."""
        for day in [1, 31]:
            d = date(2020, 1, day)
            kt = generate_company(reg_date=d, formatted=False)
            info = parse(kt)
            assert info.birth_date == d
            dd = int(kt[:2])
            assert dd == day + 40
