"""
Data output/writing utilities.

This module provides functions to export DataFrames and reports
to various formats with consistent options.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import register_function


@register_function(
    name="export_parquet",
    category="Input/Output",
    module="io.writers",
)
def export_parquet(
    df: pd.DataFrame,
    path: str | Path,
    **kwargs: Any,
) -> None:
    """
    Export DataFrame as parquet.

    Parquet is a highly compressed columnar format suitable for
    large analytical datasets. Requires pyarrow or fastparquet.

    Args:
        df (pd.DataFrame): DataFrame to export
        path (str or Path): Output file path
        **kwargs: Additional arguments passed to df.to_parquet()

    Raises:
        TypeError: If input is not a DataFrame
        ImportError: If required library (pyarrow) not installed
        IOError: If file cannot be written

    Example:
        >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        >>> export_parquet(df, 'output.parquet')
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        df.to_parquet(path, **kwargs)
    except ImportError as e:
        raise ImportError(
            "Parquet export requires 'pyarrow'. Install with: pip install pyarrow"
        ) from e

    audit_log("export_parquet", before=None, after=None)


@register_function(
    name="export_validation_report",
    category="Input/Output",
    module="io.writers",
)
def export_validation_report(
    report: Dict[str, Any],
    path: str | Path,
) -> None:
    """
    Export a validation or profiling report as JSON.

    Saves structured reports (validation results, profiling summaries, etc.)
    in machine-readable JSON format.

    Args:
        report (dict): Report dictionary to export
        path (str or Path): Output JSON file path

    Raises:
        TypeError: If report is not a dictionary
        IOError: If file cannot be written
        ValueError: If report contains non-serializable objects

    Example:
        >>> report = {'total_rows': 1000, 'missing': 5, 'status': 'PASS'}
        >>> export_validation_report(report, 'validation_report.json')
    """
    if not isinstance(report, dict):
        raise TypeError("Report must be a dictionary")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "w") as f:
            json.dump(report, f, indent=2, default=str)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Report contains non-serializable objects: {e}") from e

    audit_log("export_validation_report", before=None, after=None)
