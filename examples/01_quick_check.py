import pandas as pd
import fda_toolkit as ftk


df = pd.DataFrame({"amount": ["£1,000", "(200)", None], "date": ["01/01/2026", "02/01/2026", ""]})

try:
    ftk.quick_check(df)
except NotImplementedError:
    print("quick_check is a stub. Implement it in fda_toolkit.reporting.profiling")
