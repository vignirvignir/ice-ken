from datetime import date

import pytest

from ice_ken.kennitala import (
    parse,
    is_valid,
    generate_personal_for_date,
    generate_company_for_date,
    random_personal,
    random_company,
    get_birth_date,
)


def test_generate_personal_for_specific_date_strict():
    d = date(1985, 7, 14)
    kt = generate_personal_for_date(d, enforce_checksum=True, formatted=False)
    info = parse(kt)
    assert info.entity_type == "individual"
    assert info.birth_date == d
    assert info.century_indicator == 9
    assert is_valid(kt, enforce_checksum=True)


def test_generate_company_for_specific_date_strict():
    d = date(2012, 3, 5)
    kt = generate_company_for_date(d, enforce_checksum=True, formatted=False)
    info = parse(kt)
    assert info.entity_type == "company"
    assert info.birth_date == d
    assert info.century_indicator == 0
    assert is_valid(kt, enforce_checksum=True)


def test_random_personal_in_range_relaxed():
    start = date(1970, 1, 1)
    end = date(1970, 12, 31)
    kt = random_personal(start, end, enforce_checksum=False, formatted=False)
    info = parse(kt, enforce_checksum=False)
    assert info.entity_type == "individual"
    assert start <= info.birth_date <= end
    assert is_valid(kt, enforce_checksum=False)


def test_random_company_in_range_relaxed():
    start = date(2005, 6, 1)
    end = date(2005, 6, 30)
    kt = random_company(start, end, enforce_checksum=False, formatted=False)
    info = parse(kt, enforce_checksum=False)
    assert info.entity_type == "company"
    assert start <= info.birth_date <= end
    assert is_valid(kt, enforce_checksum=False)


def test_get_birth_date_helper_matches_parse():
    d = date(1999, 12, 31)
    kt = generate_personal_for_date(d, enforce_checksum=True, formatted=False)
    assert get_birth_date(kt) == d


def test_range_validation_errors():
    start = date(2020, 1, 2)
    end = date(2020, 1, 1)
    with pytest.raises(ValueError):
        random_personal(start, end)
    with pytest.raises(ValueError):
        random_company(start, end)
