from __future__ import annotations

from typing import Any, Dict

from fda_toolkit.features.datetime import (
    extract_date_features,
    create_period_keys,
    create_fiscal_calendar_features,
    lag_features,
)
from fda_toolkit.features.categorical import (
    limit_cardinality,
    rare_category_handler,
    encode_categorical_variables,
)


def get_registry() -> Dict[str, Dict[str, Any]]:
    return {
        "extract_date_features": {
            "callable": extract_date_features,
            "category": "Date and Time Feature Engineering",
            "module": "features.datetime",
            "description": "Extract date features.",
        },
        "create_period_keys": {
            "callable": create_period_keys,
            "category": "Date and Time Feature Engineering",
            "module": "features.datetime",
            "description": "Create period keys.",
        },
        "create_fiscal_calendar_features": {
            "callable": create_fiscal_calendar_features,
            "category": "Date and Time Feature Engineering",
            "module": "features.datetime",
            "description": "Create fiscal calendar features.",
        },
        "lag_features": {
            "callable": lag_features,
            "category": "Date and Time Feature Engineering",
            "module": "features.datetime",
            "description": "Create lag features.",
        },
        "limit_cardinality": {
            "callable": limit_cardinality,
            "category": "Categorical Handling and Encoding",
            "module": "features.categorical",
            "description": "Limit cardinality to top categories.",
        },
        "rare_category_handler": {
            "callable": rare_category_handler,
            "category": "Categorical Handling and Encoding",
            "module": "features.categorical",
            "description": "Handle rare categories.",
        },
        "encode_categorical_variables": {
            "callable": encode_categorical_variables,
            "category": "Categorical Handling and Encoding",
            "module": "features.categorical",
            "description": "Encode categorical variables.",
        },
    }
