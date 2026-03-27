"""ice_ken

Utilities for managing Icelandic national IDs (kennitala).

This package provides helpers to normalize, validate, format, and
safely mask kennitala values, as well as generation utilities.
"""

from .kennitala import (
    normalize,
    is_valid,
    parse,
    format_kennitala,
    mask,
    is_company,
    is_personal,
    is_dataset_id,
    ParsedKennitala,
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

__all__ = [
    "normalize",
    "is_valid",
    "parse",
    "format_kennitala",
    "mask",
    "is_company",
    "is_personal",
    "is_dataset_id",
    "ParsedKennitala",
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

__version__ = "0.1.0"
