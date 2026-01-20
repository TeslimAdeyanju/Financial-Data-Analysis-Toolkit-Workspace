from __future__ import annotations

from typing import Any, Dict

from fda_toolkit.io.readers import read_csv_safely, read_excel_safely, chunked_processing
from fda_toolkit.io.writers import export_parquet, export_validation_report


def get_registry() -> Dict[str, Dict[str, Any]]:
    return {
        "read_csv_safely": {
            "callable": read_csv_safely,
            "category": "IO",
            "module": "io.readers",
            "description": "Read CSV with safe defaults.",
        },
        "read_excel_safely": {
            "callable": read_excel_safely,
            "category": "IO",
            "module": "io.readers",
            "description": "Read Excel with safe defaults.",
        },
        "export_parquet": {
            "callable": export_parquet,
            "category": "IO",
            "module": "io.writers",
            "description": "Export dataframe to parquet.",
        },
        "export_validation_report": {
            "callable": export_validation_report,
            "category": "IO",
            "module": "io.writers",
            "description": "Export report to JSON.",
        },
        "chunked_processing": {
            "callable": chunked_processing,
            "category": "IO",
            "module": "io.readers",
            "description": "Process large CSV files in chunks.",
        },
    }
