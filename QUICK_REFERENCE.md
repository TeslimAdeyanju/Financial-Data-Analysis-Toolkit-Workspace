# FDA Toolkit - Quick Reference Guide

## Installation & Setup

```bash
# Install the package
pip install -e .

# Import the toolkit
import fda_toolkit as ftk
import pandas as pd
```

---

## Quick Start Examples

### 1. Load and Profile Data
```python
# Read CSV safely
df = ftk.read_csv_safely('data.csv')

# Quick diagnosis
ftk.quick_check(df)

# Detailed profile
profile = ftk.profile_report(df)
print(profile['summary'])
```

### 2. Clean Data in One Line
```python
# Generic cleaning
clean_df = ftk.quick_clean(df)

# Finance-specific cleaning
clean_df = ftk.quick_clean_finance(
    df,
    primary_key='invoice_id',
    date_cols=['date', 'due_date'],
    currency_cols=['amount', 'tax']
)
```

### 3. Discover Available Functions
```python
# All functions
all_funcs = ftk.info()

# Filter by category
core_funcs = ftk.info(category='Data Quality')

# List with details
print(all_funcs[['function', 'category', 'module']])
```

---

## Common Tasks

### Column Cleaning
```python
from fda_toolkit.core.columns import clean_column_headers

df = clean_column_headers(df)  # 'Name ' → 'name'
```

### Type Conversion
```python
from fda_toolkit.core.types import clean_numeric_column

df['amount'] = clean_numeric_column(df['amount'])  # '$1,234.56' → 1234.56
```

### Handle Missing Values
```python
from fda_toolkit.core.missing import coerce_empty_to_nan, fill_missing

df = coerce_empty_to_nan(df)  # 'na' → NaN
df = fill_missing(df, strategy='mean')  # Fill with column mean
```

### Remove Duplicates
```python
from fda_toolkit.core.duplicates import remove_duplicates

df = remove_duplicates(df, subset=['id'])  # Keep first occurrence
```

### Detect Outliers
```python
from fda_toolkit.core.outliers import flag_outliers

df = flag_outliers(df, column='amount', method='iqr')
# Creates 'is_outlier' column with True/False
```

### Finance-Specific
```python
from fda_toolkit.finance.parsing import parse_currency

df['amount'] = parse_currency(df['amount'])  # Parse currencies

from fda_toolkit.finance.entities import strip_legal_suffixes

df['vendor'] = strip_legal_suffixes(df['vendor'])  # 'ACME Ltd' → 'ACME'
```

### Validate Data
```python
from fda_toolkit.validation.schema import validate_required_fields
from fda_toolkit.validation.ranges import validate_data_ranges

# Check required columns
validate_required_fields(df, ['id', 'date', 'amount'])

# Check value ranges
violations = validate_data_ranges(
    df, 
    {'amount': (0, 1_000_000), 'age': (0, 120)}
)
```

### Feature Engineering
```python
from fda_toolkit.features.datetime import extract_date_features
from fda_toolkit.features.categorical import limit_cardinality

df = extract_date_features(df, 'date')  # Adds year, month, quarter cols
df['category'] = limit_cardinality(df['category'], top_n=10)  # Keep top 10
```

### Export Results
```python
ftk.export_parquet(df, 'output.parquet')
ftk.export_validation_report(report_dict, 'validation.json')
```

---

## Function Categories

| Category | Count | Purpose |
|----------|-------|---------|
| **Column Management** | 2 | Header cleaning & deduplication |
| **Data Quality** | 8 | Duplicates, missing values |
| **Outlier Detection** | 6 | Statistical outlier methods |
| **Type Conversion** | 4 | Numeric, date, boolean parsing |
| **Text Processing** | 3 | Text & categorical cleaning |
| **Feature Engineering** | 7 | Date & categorical features |
| **Finance** | 11 | Currency, entities, validation |
| **Validation** | 8 | Schema, ranges, integrity |
| **Input/Output** | 5 | Safe read/write operations |
| **Reporting** | 10 | Profiling, snapshots, info |
| **Utilities** | 3 | Memory, security, logging |

---

## Module Mapping

```
Quick Start                     → ftk.quick_clean()
                                → ftk.quick_check()

Column Cleaning                 → ftk.core.columns
Type Conversion                 → ftk.core.types
Duplicate Handling              → ftk.core.duplicates
Missing Values                  → ftk.core.missing
Outlier Detection               → ftk.core.outliers
Text Processing                 → ftk.core.text

Date Features                   → ftk.features.datetime
Categorical Features            → ftk.features.categorical

Currency Parsing                → ftk.finance.parsing
Entity Standardization          → ftk.finance.entities
Financial Validation            → ftk.finance.rules

Data Reading                    → ftk.io.readers
Data Writing                    → ftk.io.writers

Schema Validation               → ftk.validation.schema
Range Validation                → ftk.validation.ranges
Integrity Checks                → ftk.validation.integrity

Data Profiling                  → ftk.reporting.profiling
Change Tracking                 → ftk.reporting.delta

Audit Logging                   → ftk.utils.logging
Data Security                   → ftk.utils.security
Memory Optimization             → ftk.utils.types
```

---

## Audit Trail

```python
from fda_toolkit.utils.logging import get_global_audit_log

# All operations are automatically logged
log = get_global_audit_log()

# Export audit trail
for event in log.events:
    print(f"{event.name} @ {event.timestamp_utc}")

# Get as JSON
audit_json = log.to_dict()
```

---

## Pipeline Example

```python
import fda_toolkit as ftk
import pandas as pd

# Load
df = ftk.read_csv_safely('transactions.csv')

# Diagnose
ftk.quick_check(df)

# Clean (generic)
df = ftk.quick_clean(df)

# Clean (finance-specific)
df = ftk.quick_clean_finance(
    df,
    primary_key='transaction_id',
    date_cols=['transaction_date'],
    currency_cols=['amount', 'tax']
)

# Validate
from fda_toolkit.validation.integrity import reconciliation_check
report = reconciliation_check(
    original_df, df, 
    value_cols=['amount'], 
    group_cols=['customer_id']
)

# Profile cleaned data
profile = ftk.profile_report(df)

# Export
ftk.export_parquet(df, 'clean_transactions.parquet')
ftk.export_validation_report(profile, 'data_profile.json')

print("✅ Pipeline complete!")
```

---

## Key Parameters

### copy=True (Default)
```python
# Returns modified copy, leaves original unchanged
df_clean = ftk.clean_column_headers(df, copy=True)
assert df.columns[0] == 'Name '  # Original unchanged
```

### errors='raise' or 'coerce'
```python
# 'raise' (default) - fail on invalid values
df = ftk.convert_data_types(df, {'id': 'int'}, errors='raise')

# 'coerce' - convert invalid to NaN
df = ftk.convert_data_types(df, {'id': 'int'}, errors='coerce')
```

### method='iqr' or 'zscore'
```python
# IQR method (Tukey's fences)
df = ftk.flag_outliers(df, 'amount', method='iqr')

# Z-score method (±3 sigma)
df = ftk.flag_outliers(df, 'amount', method='zscore')
```

---

## Error Handling

```python
import pandas as pd
from fda_toolkit.core.columns import clean_column_headers

try:
    # All functions validate inputs
    df = "not a dataframe"
    clean_column_headers(df)
except TypeError as e:
    print(f"Type error: {e}")  # "Input must be a pandas DataFrame"

try:
    df = pd.DataFrame({'A': [1, 2]})
    df = clean_column_headers(df, lowercase=True)
except Exception as e:
    print(f"Error: {e}")
```

---

## Testing Your Code

```python
import pytest
import pandas as pd
from fda_toolkit.core.columns import clean_column_headers

def test_clean_headers():
    df = pd.DataFrame({'Name ': [1], 'Age (years)': [2]})
    result = clean_column_headers(df)
    assert result.columns.tolist() == ['name', 'age_years']

if __name__ == '__main__':
    test_clean_headers()
    print("✅ Test passed!")
```

---

## Performance Tips

1. **Use chunked_processing for large files:**
   ```python
   for chunk in ftk.chunked_processing('huge_file.csv', chunksize=50_000):
       process(chunk)
   ```

2. **Optimize memory:**
   ```python
   from fda_toolkit.utils.types import optimize_dtypes
   df = optimize_dtypes(df)  # Can reduce memory by 50%+
   ```

3. **Use parquet for speed:**
   ```python
   ftk.export_parquet(df, 'data.parquet')  # Faster, compressed
   df = pd.read_parquet('data.parquet')
   ```

---

## Documentation

- **Function reference**: `ftk.info()`
- **Data summary**: `ftk.get_data_summary(df)`
- **Type report**: `ftk.infer_and_report_types(df)`
- **Missing values**: `ftk.missingness_profile(df)`
- **Memory usage**: `ftk.memory_profile(df)`
- **Full profile**: `ftk.profile_report(df)`

---

## Support

For issues or questions:
- Check `ftk.info()` for available functions
- Review function docstrings: `help(ftk.quick_clean)`
- Look at examples in docstrings
- Check IMPLEMENTATION_SUMMARY.md for module details

---

## Version Info

```python
import fda_toolkit
print(fda_toolkit.__version__)  # If defined in __init__.py
```

Happy data cleaning! 🚀
