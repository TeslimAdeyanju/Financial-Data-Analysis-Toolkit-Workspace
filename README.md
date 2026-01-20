FDA Toolkit

Purpose
A practical Python package scaffold for Financial Data Analyst workflows.
It focuses on predictable ingestion, cleaning, profiling, validation, finance specific parsing, and one line pipelines.

Install editable
pip install -e .

Quick start

import fda_toolkit as ftk

df = ftk.read_csv_safely("data/transactions.csv")
ftk.quick_check(df)

df_clean = ftk.quick_clean_finance(
    df,
    primary_key="transaction_id",
    date_cols=["transaction_date"],
    currency_cols=["amount"],
)

Design
Functions are grouped by your categories.
A registry powers info and allows you to keep modules dynamic as the library grows.

Run tests
pytest
