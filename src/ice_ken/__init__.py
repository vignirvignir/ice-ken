"""ice_ken

Utilities for managing Icelandic national IDs (kennitala).

This package provides helpers to normalize, validate, format, and
safely mask kennitala values.
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
]

__version__ = "0.1.0"
