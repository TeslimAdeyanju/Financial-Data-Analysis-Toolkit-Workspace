"""
Data input/reading utilities.

This module provides functions to safely read data from CSV, Excel,
and other formats with sensible defaults and error handling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Generator

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="read_csv_safely",
    category="Input/Output",
    module="io.readers",
)
def read_csv_safely(
    path: str | Path,
    encoding: Optional[str] = None,
    dtype: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Read CSV with safe defaults.

    Applies consistent encoding detection, NA value handling, and
    optional dtype specifications for reliable data ingestion.

    Args:
        path (str or Path): Path to CSV file
        encoding (str): File encoding. Default: detect automatically
        dtype (dict): Column dtype mapping. Default: None
        **kwargs: Additional arguments passed to pd.read_csv()

    Returns:
        pd.DataFrame: Loaded DataFrame

    Raises:
        FileNotFoundError: If file does not exist
        pd.errors.ParserError: If CSV cannot be parsed

    Example:
        >>> df = read_csv_safely('data.csv', dtype={'id': 'int64'})
        >>> df.shape
        (1000, 10)
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    na_values = kwargs.pop("na_values", ["", "NA", "na", "N/A", "null", "NULL"])

    df = pd.read_csv(
        path,
        encoding=encoding,
        dtype=dtype,
        na_values=na_values,
        **kwargs,
    )

    audit_log("read_csv_safely", before=None, after=df)
    return df


@register_function(
    name="read_excel_safely",
    category="Input/Output",
    module="io.readers",
)
def read_excel_safely(
    path: str | Path,
    sheet_name: str | int | None = 0,
    dtype: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Read Excel with safe defaults.

    Handles sheet selection, dtype specifications, and consistent
    missing value interpretation.

    Args:
        path (str or Path): Path to Excel file
        sheet_name (str or int): Sheet name or index. Default: 0 (first sheet)
        dtype (dict): Column dtype mapping. Default: None
        **kwargs: Additional arguments passed to pd.read_excel()

    Returns:
        pd.DataFrame: Loaded DataFrame

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If sheet not found
        ImportError: If openpyxl not installed

    Example:
        >>> df = read_excel_safely('data.xlsx', sheet_name='Sheet1')
        >>> df.shape
        (500, 15)
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    na_values = kwargs.pop("na_values", ["", "NA", "na", "N/A", "null", "NULL"])

    df = pd.read_excel(
        path,
        sheet_name=sheet_name,
        dtype=dtype,
        na_values=na_values,
        **kwargs,
    )

    audit_log("read_excel_safely", before=None, after=df)
    return df


@register_function(
    name="chunked_processing",
    category="Input/Output",
    module="io.readers",
)
def chunked_processing(
    path: str | Path,
    chunksize: int = 100_000,
    **kwargs: Any,
) -> Generator[pd.DataFrame, None, None]:
    """
    Yield chunks of a CSV for large datasets.

    Processes large CSV files in chunks to avoid loading entire
    dataset into memory.

    Args:
        path (str or Path): Path to CSV file
        chunksize (int): Number of rows per chunk. Default: 100,000
        **kwargs: Additional arguments passed to pd.read_csv()

    Yields:
        pd.DataFrame: Chunks of the data

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If chunksize is not positive

    Example:
        >>> for chunk in chunked_processing('large_file.csv', chunksize=50_000):
        ...     process_chunk(chunk)
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if chunksize <= 0:
        raise ValueError("chunksize must be positive")

    na_values = kwargs.pop("na_values", ["", "NA", "na", "N/A", "null", "NULL"])

    for chunk in pd.read_csv(
        path,
        chunksize=chunksize,
        na_values=na_values,
        **kwargs,
    ):
        audit_log("chunked_processing", before=None, after=chunk)
        yield chunk
