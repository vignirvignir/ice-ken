import pytest

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
    generate_personal,
    generate_company,
)


# Known valid personal kennitala (strict): 120160-3389
VALID_PERSONAL = "120160-3389"
VALID_PERSONAL_DIGITS = "1201603389"

# Fabricated company kennitala (day + 40 => 52). Checksum not enforced in relaxed mode.
COMPANY_RELAXED = "520160-3379"
COMPANY_RELAXED_DIGITS = "5201603379"


def test_normalize_strips_non_digits():
    assert normalize(" 120160-3389 ") == VALID_PERSONAL_DIGITS
    assert normalize("12 01 60  -  3389") == VALID_PERSONAL_DIGITS


def test_format_kennitala_success_and_errors():
    assert format_kennitala(VALID_PERSONAL_DIGITS) == VALID_PERSONAL
    with pytest.raises(ValueError):
        format_kennitala("123")


def test_is_valid_strict_and_relaxed_personal():
    assert is_valid(VALID_PERSONAL) is True
    # Alter checksum to force failure in strict mode but pass in relaxed
    bad_checksum = "120160-3379"
    assert is_valid(bad_checksum) is False
    assert is_valid(bad_checksum, enforce_checksum=False) is True


def test_is_valid_relaxed_company_and_entity_detection():
    # Company example: day=52 (12 + 40), relaxed validation only
    assert is_company(COMPANY_RELAXED) is True
    assert is_personal(COMPANY_RELAXED) is False
    assert is_valid(COMPANY_RELAXED, enforce_checksum=False) is True


def test_parse_strict_and_relaxed():
    info = parse(VALID_PERSONAL)
    assert isinstance(info, ParsedKennitala)
    assert info.digits == VALID_PERSONAL_DIGITS
    assert info.formatted == VALID_PERSONAL
    assert (
        info.birth_date.year == 1960
        and info.birth_date.month == 1
        and info.birth_date.day == 12
    )
    assert info.century_indicator == 9
    assert info.entity_type == "individual"

    # Strict parse should fail for checksum-failing variant
    with pytest.raises(ValueError):
        parse("120160-3379")

    # Relaxed parse should succeed for company example
    company_info = parse(COMPANY_RELAXED, enforce_checksum=False)
    assert company_info.formatted == COMPANY_RELAXED
    assert company_info.entity_type == "company"
    # Day should resolve to 12 after subtracting 40
    assert company_info.birth_date.day == 12


def test_mask_output():
    assert mask(VALID_PERSONAL) == "******-3389"
    # With tail=2, remaining masked head is split across the hyphen
    assert mask(VALID_PERSONAL, visible_tail=2) == "******-**89"
    # visible_tail=0 means full mask, split across the hyphen
    assert mask(VALID_PERSONAL, visible_tail=0) == "******-****"


def test_invalid_inputs_length_and_century():
    # Not enough digits
    assert is_valid("123456789") is False
    # Invalid century indicator (10th digit not in {8,9,0})
    invalid_century = VALID_PERSONAL_DIGITS[:-1] + "1"
    assert is_valid(invalid_century, enforce_checksum=False) is False


def test_invalid_date_detection():
    # 320160-... (day 32) personal should fail date check (strict/relaxed)
    bad_date_digits = "3201603389"
    assert is_valid(bad_date_digits, enforce_checksum=False) is False


def test_invalid_month_detection():
    # Month 13 should fail date validation
    bad_month_digits = "1213603389"  # DD=12, MM=13, YY=60
    assert is_valid(bad_month_digits, enforce_checksum=False) is False
    # Month 00 should fail
    bad_month_zero = "1200603389"  # DD=12, MM=00, YY=60
    assert is_valid(bad_month_zero, enforce_checksum=False) is False


def test_century_indicators_2000s_and_1800s_relaxed():
    # 2000s: century indicator 0 → year 2001
    digits_2001 = "1201012000"  # 12-01-01, seq=20, p=0, c=0
    info2000 = parse(digits_2001, enforce_checksum=False)
    assert info2000.century_indicator == 0
    assert info2000.birth_date.year == 2001
    assert info2000.entity_type == "individual"

    # 1800s: century indicator 8 → year 1888
    digits_1888 = "1506882008"  # 15-06-88, seq=20, p=0, c=8
    info1800 = parse(digits_1888, enforce_checksum=False)
    assert info1800.century_indicator == 8
    assert info1800.birth_date.year == 1888


def test_company_day_extremes_resolve_correctly_relaxed():
    # DD=41 → actual day 1
    digits_day41 = "4101012000"
    info41 = parse(digits_day41, enforce_checksum=False)
    assert info41.entity_type == "company"
    assert info41.birth_date.day == 1

    # DD=71 → actual day 31
    digits_day71 = "7101012000"
    info71 = parse(digits_day71, enforce_checksum=False)
    assert info71.entity_type == "company"
    assert info71.birth_date.day == 31


def test_generate_personal_and_company():
    # Generate several personal IDs and validate
    for _ in range(5):
        kt = generate_personal(enforce_checksum=True)
        assert is_personal(kt)
        assert is_valid(kt)

    # Relaxed: checksum may fail but structure/date should pass
    for _ in range(5):
        kt = generate_personal(enforce_checksum=False)
        assert is_personal(kt)
        assert is_valid(kt, enforce_checksum=False)

    # Company generation strict and relaxed
    for _ in range(5):
        kt = generate_company(enforce_checksum=True)
        assert is_company(kt)
        assert is_valid(kt)

    for _ in range(5):
        kt = generate_company(enforce_checksum=False)
        assert is_company(kt)
        assert is_valid(kt, enforce_checksum=False)

    # Relaxed-generated IDs should typically fail strict checksum
    for _ in range(5):
        kt_relaxed = generate_personal(enforce_checksum=False)
        assert is_valid(kt_relaxed) is False
    for _ in range(5):
        kt_relaxed_c = generate_company(enforce_checksum=False)
        assert is_valid(kt_relaxed_c) is False

    # Unformatted output should be 10 digits without hyphen
    kt_person_digits = generate_personal(enforce_checksum=True, formatted=False)
    assert len(kt_person_digits) == 10 and "-" not in kt_person_digits
    assert 1 <= int(kt_person_digits[:2]) <= 31
    assert is_personal(kt_person_digits)
    assert is_valid(kt_person_digits) is True

    kt_company_digits = generate_company(enforce_checksum=True, formatted=False)
    assert len(kt_company_digits) == 10 and "-" not in kt_company_digits
    assert 41 <= int(kt_company_digits[:2]) <= 71
    assert is_company(kt_company_digits)
    assert is_valid(kt_company_digits) is True


def test_is_dataset_id_helper():
    # Positive cases with markers in positions 7-8
    assert is_dataset_id("120160-1489") is True
    assert is_dataset_id("520160-1579") is True  # company-formatted variant
    # Hyphenless form should also be accepted
    assert is_dataset_id("1201601489") is True
    # Negative cases
    assert is_dataset_id(VALID_PERSONAL) is False
    assert is_dataset_id("123") is False


def test_mask_errors_on_bad_length():
    with pytest.raises(ValueError):
        mask("123")
