"""Tests for src/cleaner.py: duplicate removal and missing-value strategies."""

import pandas as pd

from src.cleaner import STRATEGY_DROP, STRATEGY_FILL, STRATEGY_LEAVE, clean_data


def test_remove_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    cleaned, summary = clean_data(df, remove_duplicates=True, missing_strategy=STRATEGY_LEAVE)
    assert len(cleaned) == 2
    assert summary["duplicates_removed"] == 1


def test_keep_duplicates_when_disabled():
    df = pd.DataFrame({"a": [1, 1, 2]})
    cleaned, summary = clean_data(df, remove_duplicates=False, missing_strategy=STRATEGY_LEAVE)
    assert len(cleaned) == 3
    assert summary["duplicates_removed"] == 0


def test_leave_missing_values_untouched():
    df = pd.DataFrame({"a": [1, None, 3]})
    cleaned, summary = clean_data(df, remove_duplicates=False, missing_strategy=STRATEGY_LEAVE)
    assert cleaned["a"].isna().sum() == 1
    assert summary["cells_filled"] == 0
    assert summary["rows_dropped_missing"] == 0


def test_drop_missing_rows():
    df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", None]})
    cleaned, summary = clean_data(df, remove_duplicates=False, missing_strategy=STRATEGY_DROP)
    assert cleaned.isna().sum().sum() == 0
    assert len(cleaned) == 1
    assert summary["rows_dropped_missing"] == 2


def test_fill_missing_numeric_with_median():
    df = pd.DataFrame({"amount": [10, 20, None, 40]})
    cleaned, summary = clean_data(df, remove_duplicates=False, missing_strategy=STRATEGY_FILL)
    assert cleaned["amount"].isna().sum() == 0
    assert cleaned.loc[2, "amount"] == 20.0
    assert summary["cells_filled"] == 1


def test_fill_missing_text_with_unknown():
    df = pd.DataFrame({"name": ["Alice", None, "Bob"]})
    cleaned, summary = clean_data(df, remove_duplicates=False, missing_strategy=STRATEGY_FILL)
    assert cleaned.loc[1, "name"] == "Unknown"
    assert summary["cells_filled"] == 1


def test_clean_empty_dataframe():
    cleaned, summary = clean_data(pd.DataFrame(), remove_duplicates=True, missing_strategy=STRATEGY_FILL)
    assert cleaned.empty
    assert summary["rows_before"] == 0
    assert summary["rows_after"] == 0


def test_clean_all_null_column_fills_unknown():
    df = pd.DataFrame({"a": [None, None, None], "b": [1, 2, 3]})
    cleaned, _ = clean_data(df, remove_duplicates=False, missing_strategy=STRATEGY_FILL)
    assert (cleaned["a"] == "Unknown").all()


def test_rows_summary_reflects_before_and_after():
    df = pd.DataFrame({"a": [1, 1, 2, None]})
    cleaned, summary = clean_data(df, remove_duplicates=True, missing_strategy=STRATEGY_DROP)
    assert summary["rows_before"] == 4
    assert summary["rows_after"] == len(cleaned)
