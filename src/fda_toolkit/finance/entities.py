"""
Entity name and reference standardization utilities.

This module provides functions to clean and normalize vendor/customer names,
legal entities, and reference codes.
"""

from __future__ import annotations

from typing import Dict, Optional

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="standardize_entity_names",
    category="Finance",
    module="finance.entities",
)
def standardize_entity_names(
    s: pd.Series,
    mapping: Dict[str, str],
    case_insensitive: bool = True,
) -> pd.Series:
    """
    Standardize vendor or customer names via mapping.

    Applies a dictionary mapping to convert variant entity names
    into standard canonical forms.

    Args:
        s (pd.Series): Input entity name Series
        mapping (dict): Dictionary mapping variant names to standard names
        case_insensitive (bool): Apply mapping case-insensitively. Default: True

    Returns:
        pd.Series: Standardized entity name Series

    Raises:
        TypeError: If Series is not object/string dtype or mapping is not dict

    Example:
        >>> s = pd.Series(['ACME Inc', 'acme incorporated', 'acme', 'Smith Ltd'])
        >>> mapping = {'acme': 'ACME Corporation', 'smith': 'Smith Group'}
        >>> standardize_entity_names(s, mapping).unique()
        array(['ACME Corporation', 'Smith Group'], dtype=object)
    """
    if s.dtype != "object":
        raise TypeError("Series must be object/string dtype")
    if not isinstance(mapping, dict):
        raise TypeError("Mapping must be a dictionary")

    s = s.copy().astype(str).str.strip()

    if case_insensitive:
        # Create case-insensitive mapping
        s_lower = s.str.lower()
        mapping_lower = {k.lower(): v for k, v in mapping.items()}
        s = s_lower.map(lambda x: mapping_lower.get(x, x))
        # Restore original case for unmapped values
        unmapped = s_lower.isin(mapping_lower.values()).apply(lambda x: not x)
        original_vals = s.where(~unmapped)
        s = s.where(unmapped, original_vals)
    else:
        s = s.map(lambda x: mapping.get(x, x))

    audit_log("standardize_entity_names", before=None, after=s)
    return s


@register_function(
    name="strip_legal_suffixes",
    category="Finance",
    module="finance.entities",
)
def strip_legal_suffixes(
    s: pd.Series,
    suffixes: tuple[str, ...] = ("ltd", "limited", "plc", "inc", "llc"),
) -> pd.Series:
    """
    Remove common legal suffixes in a controlled way.

    Removes legal entity type indicators while preserving the core
    company name.

    Args:
        s (pd.Series): Input entity name Series
        suffixes (tuple): Suffixes to remove. Default: common corporate suffixes

    Returns:
        pd.Series: Entity names with suffixes removed

    Raises:
        TypeError: If Series is not object/string dtype

    Example:
        >>> s = pd.Series(['ACME Limited', 'Smith & Co Inc', 'Jones LLC'])
        >>> strip_legal_suffixes(s).tolist()
        ['ACME', 'Smith & Co', 'Jones']
    """
    if s.dtype != "object":
        raise TypeError("Series must be object/string dtype")

    s = s.copy().astype(str).str.strip()

    for suffix in suffixes:
        # Remove suffix at end (case-insensitive)
        pattern = f"\\s+{suffix}\\s*$"
        s = s.str.replace(pattern, "", flags=2, regex=True)

    s = s.str.strip()

    audit_log("strip_legal_suffixes", before=None, after=s)
    return s


@register_function(
    name="normalize_reference_codes",
    category="Finance",
    module="finance.entities",
)
def normalize_reference_codes(
    s: pd.Series,
    keep_alnum_only: bool = True,
    upper: bool = True,
) -> pd.Series:
    """
    Normalize invoice numbers, PO numbers, and references.

    Standardizes formatting of reference codes by removing special characters
    and applying consistent casing.

    Args:
        s (pd.Series): Input reference code Series
        keep_alnum_only (bool): Keep only alphanumeric characters. Default: True
        upper (bool): Convert to uppercase. Default: True

    Returns:
        pd.Series: Normalized reference code Series

    Raises:
        TypeError: If Series is not object/string dtype

    Example:
        >>> s = pd.Series(['INV-2024-001', 'inv_2024-002', 'inv.2024.003'])
        >>> normalize_reference_codes(s).unique()
        array(['INV2024001', 'INV2024002', 'INV2024003'], dtype=object)
    """
    if s.dtype != "object":
        raise TypeError("Series must be object/string dtype")

    s = s.copy().astype(str).str.strip()

    if keep_alnum_only:
        s = s.str.replace(r"[^a-zA-Z0-9]", "", regex=True)

    if upper:
        s = s.str.upper()

    audit_log("normalize_reference_codes", before=None, after=s)
    return s
