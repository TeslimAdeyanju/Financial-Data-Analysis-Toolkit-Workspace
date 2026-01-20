"""
Text cleaning and standardization utilities.

This module provides functions to clean free text and standardize
categorical text values for reliable analysis.
"""

from __future__ import annotations

from typing import Dict, Iterable, Optional

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="clean_text_column",
    category="Text Processing",
    module="core.text",
)
def clean_text_column(
    s: pd.Series,
    strip: bool = True,
    to_lower: bool = False,
    normalize_whitespace: bool = True,
) -> pd.Series:
    """
    Clean free text while preserving meaning.

    Performs whitespace handling, optional case conversion, and
    removes extra spaces between words.

    Args:
        s (pd.Series): Input text Series
        strip (bool): Strip leading/trailing whitespace. Default: True
        to_lower (bool): Convert to lowercase. Default: False
        normalize_whitespace (bool): Normalize multiple spaces to single space. Default: True

    Returns:
        pd.Series: Cleaned text Series

    Raises:
        TypeError: If Series is not object/string dtype

    Example:
        >>> s = pd.Series(['  HELLO  WORLD  ', 'test'])
        >>> clean_text_column(s, strip=True, normalize_whitespace=True).tolist()
        ['HELLO WORLD', 'test']
    """
    if s.dtype != "object":
        raise TypeError("Series must be object/string dtype")

    s = s.copy().astype(str)

    if strip:
        s = s.str.strip()

    if to_lower:
        s = s.str.lower()

    if normalize_whitespace:
        s = s.str.replace(r"\s+", " ", regex=True)

    audit_log("clean_text_column", before=None, after=s)
    return s


@register_function(
    name="standardize_text_values",
    category="Text Processing",
    module="core.text",
)
def standardize_text_values(
    s: pd.Series,
    mapping: Dict[str, str],
    case_insensitive: bool = True,
) -> pd.Series:
    """
    Standardize text values using an explicit mapping.

    Applies a dictionary mapping to convert variant text values
    into standard forms.

    Args:
        s (pd.Series): Input text Series
        mapping (dict): Dictionary mapping old values to new values
        case_insensitive (bool): Apply mapping case-insensitively. Default: True

    Returns:
        pd.Series: Standardized text Series

    Raises:
        TypeError: If Series is not object/string dtype or mapping is not dict

    Example:
        >>> s = pd.Series(['Yes', 'YES', 'no', 'N'])
        >>> standardize_text_values(s, {'yes': 'Y', 'no': 'N'})
        0    Y
        1    Y
        2    N
        3    N
    """
    if s.dtype != "object":
        raise TypeError("Series must be object/string dtype")
    if not isinstance(mapping, dict):
        raise TypeError("Mapping must be a dictionary")

    s = s.copy().astype(str)

    if case_insensitive:
        # Create case-insensitive mapping
        s_lower = s.str.lower()
        mapping_lower = {k.lower(): v for k, v in mapping.items()}
        s = s_lower.map(lambda x: mapping_lower.get(x, x))
    else:
        s = s.map(lambda x: mapping.get(x, x))

    audit_log("standardize_text_values", before=None, after=s)
    return s


@register_function(
    name="clean_categorical_column",
    category="Text Processing",
    module="core.text",
)
def clean_categorical_column(
    s: pd.Series,
    strip: bool = True,
    to_upper: bool = False,
    to_lower: bool = True,
) -> pd.Series:
    """
    Clean categorical text values into a stable form.

    Applies consistent normalization for categorical variables,
    making them suitable for grouping and analysis.

    Args:
        s (pd.Series): Input categorical Series
        strip (bool): Strip whitespace. Default: True
        to_upper (bool): Convert to uppercase. Default: False
        to_lower (bool): Convert to lowercase. Default: True (overrides to_upper)

    Returns:
        pd.Series: Cleaned categorical Series

    Raises:
        TypeError: If Series is not object/string dtype

    Example:
        >>> s = pd.Series(['  Category A  ', '  category a  '])
        >>> clean_categorical_column(s).unique()
        array(['category a'], dtype=object)
    """
    if s.dtype != "object":
        raise TypeError("Series must be object/string dtype")

    s = s.copy().astype(str)

    if strip:
        s = s.str.strip()

    if to_lower:
        s = s.str.lower()
    elif to_upper:
        s = s.str.upper()

    audit_log("clean_categorical_column", before=None, after=s)
    return s
