import fda_toolkit as ftk


def test_imports_exist():
    assert hasattr(ftk, "info")
    assert hasattr(ftk, "quick_clean")
    assert hasattr(ftk, "read_csv_safely")
