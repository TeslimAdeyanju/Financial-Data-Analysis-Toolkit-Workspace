"""
Financial data parsing utilities.

This module provides functions to parse currency, percentage, and
accounting notation values into clean numeric formats.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
import re

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="parse_currency",
    category="Finance",
    module="finance.parsing",
)
def parse_currency(
    s: pd.Series,
    currency_symbols: tuple[str, ...] = ("£", "$", "€", "₦"),
    thousands: str = ",",
    decimal: str = ".",
) -> pd.Series:
    """
    Parse currency strings into numeric values.

    Removes currency symbols, handles thousands separators,
    and converts to numeric type.

    Args:
        s (pd.Series): Input currency string Series
        currency_symbols (tuple): Symbols to remove. Default: common currencies
        thousands (str): Thousands separator. Default: ","
        decimal (str): Decimal separator. Default: "."

    Returns:
        pd.Series: Numeric Series

    Raises:
        TypeError: If Series is not object/string dtype

    Example:
        >>> s = pd.Series(['$1,234.56', '€5,678.90'])
        >>> parse_currency(s).tolist()
        [1234.56, 5678.9]
    """
    if s.dtype != "object":
        raise TypeError("Series must be object/string dtype")

    s = s.copy().astype(str)

    # Remove currency symbols
    for symbol in currency_symbols:
        s = s.str.replace(symbol, "", regex=False)

    # Remove thousands separator and normalize decimal
    s = s.str.replace(thousands, "", regex=False)
    s = s.str.replace(decimal, ".", regex=False)

    # Convert to numeric
    s = pd.to_numeric(s, errors="coerce")

    audit_log("parse_currency", before=None, after=s)
    return s


@register_function(
    name="parse_percentage",
    category="Finance",
    module="finance.parsing",
)
def parse_percentage(
    s: pd.Series,
    assume_percent_sign_means_100: bool = True,
) -> pd.Series:
    """
    Parse percentages into a consistent numeric scale.

    Handles values like "25.5%" or "0.255" and normalizes to
    either decimal (0.255) or percentage (25.5) scale.

    Args:
        s (pd.Series): Input percentage string Series
        assume_percent_sign_means_100 (bool): If True, "25.5%" becomes 0.255.
                                              If False, becomes 25.5. Default: True

    Returns:
        pd.Series: Numeric Series

    Raises:
        TypeError: If Series is not object/string dtype

    Example:
        >>> s = pd.Series(['25.5%', '0.255', '12%'])
        >>> parse_percentage(s).tolist()
        [0.255, 0.255, 0.12]
    """
    if s.dtype != "object":
        raise TypeError("Series must be object/string dtype")

    s = s.copy().astype(str).str.strip()

    # Identify which values have % sign
    has_percent = s.str.contains("%", regex=False)

    # Remove % sign
    s = s.str.replace("%", "", regex=False)

    # Convert to numeric
    s = pd.to_numeric(s, errors="coerce")

    # Scale appropriately
    if assume_percent_sign_means_100:
        s = s.where(~has_percent, s / 100)

    audit_log("parse_percentage", before=None, after=s)
    return s


@register_function(
    name="clean_accounting_negative",
    category="Finance",
    module="finance.parsing",
)
def clean_accounting_negative(s: pd.Series) -> pd.Series:
    """
    Convert accounting negatives such as (123.45) into -123.45.

    Handles the accounting convention where negative numbers are
    enclosed in parentheses.

    Args:
        s (pd.Series): Input string or numeric Series

    Returns:
        pd.Series: Numeric Series with negatives properly signed

    Example:
        >>> s = pd.Series(['(123.45)', '456.78', '(10)'])
        >>> clean_accounting_negative(s).tolist()
        [-123.45, 456.78, -10.0]
    """
    s = s.copy().astype(str)

    # Find values in parentheses
    in_parens = s.str.contains(r"^\(.*\)$", regex=True)

    # Remove parentheses and convert to numeric
    s = s.str.replace(r"^\((.+)\)$", "-\\1", regex=True)
    s = pd.to_numeric(s, errors="coerce")

    audit_log("clean_accounting_negative", before=None, after=s)
    return s
