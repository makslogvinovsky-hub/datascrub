"""Tests for src/data_profiler.py: type detection, missing values, duplicates,
warnings, and basic statistics."""

import pandas as pd

from src.data_profiler import (
    CATEGORICAL,
    DATETIME,
    MIXED,
    NUMERIC,
    detect_column_types,
    duplicate_summary,
    missing_value_summary,
    numeric_statistics,
    quality_warnings,
    total_missing,
)


def test_detect_numeric_column():
    df = pd.DataFrame({"amount": [1, 2, 3, 4]})
    assert detect_column_types(df)["amount"] == NUMERIC


def test_detect_numeric_strings():
    df = pd.DataFrame({"amount": ["1", "2", "3", "4"]})
    assert detect_column_types(df)["amount"] == NUMERIC


def test_detect_categorical_column():
    df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"]})
    assert detect_column_types(df)["name"] == CATEGORICAL


def test_detect_datetime_strings():
    df = pd.DataFrame({"date": ["2024-01-01", "2024-02-01", "2024-03-01"]})
    assert detect_column_types(df)["date"] == DATETIME


def test_detect_mixed_column():
    df = pd.DataFrame({"col": ["10", "abc", "20", "xyz", "thirty"]})
    assert detect_column_types(df)["col"] == MIXED


def test_detect_all_null_column():
    df = pd.DataFrame({"col": [None, None, None]})
    assert detect_column_types(df)["col"] == MIXED


def test_detect_empty_dataframe():
    assert detect_column_types(pd.DataFrame()) == {}


def test_detect_single_value_column():
    df = pd.DataFrame({"only": [5, 5, 5]})
    assert detect_column_types(df)["only"] == NUMERIC


def test_missing_value_summary_counts():
    df = pd.DataFrame({"a": [1, None, 3], "b": [None, None, "x"]})
    summary = missing_value_summary(df)
    row_a = summary[summary["Column"] == "a"].iloc[0]
    row_b = summary[summary["Column"] == "b"].iloc[0]
    assert row_a["Missing Count"] == 1
    assert row_b["Missing Count"] == 2


def test_missing_value_summary_empty_df():
    assert missing_value_summary(pd.DataFrame()).empty


def test_total_missing():
    df = pd.DataFrame({"a": [1, None], "b": [None, None]})
    assert total_missing(df) == 3


def test_duplicate_summary():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    result = duplicate_summary(df)
    assert result["duplicate_count"] == 1
    assert result["duplicate_percentage"] == round(1 / 3 * 100, 1)


def test_duplicate_summary_empty_df():
    assert duplicate_summary(pd.DataFrame()) == {"duplicate_count": 0, "duplicate_percentage": 0.0}


def test_quality_warnings_high_missing():
    df = pd.DataFrame({"a": [1, None, None, None]})
    warnings = quality_warnings(df, detect_column_types(df))
    assert any("missing" in w for w in warnings)


def test_quality_warnings_constant_column():
    df = pd.DataFrame({"a": [5, 5, 5]})
    warnings = quality_warnings(df, detect_column_types(df))
    assert any("constant" in w for w in warnings)


def test_quality_warnings_mixed_column():
    df = pd.DataFrame({"a": ["10", "abc", "20", "xyz"]})
    warnings = quality_warnings(df, detect_column_types(df))
    assert any("mixed" in w for w in warnings)


def test_quality_warnings_empty_df():
    assert quality_warnings(pd.DataFrame(), {}) == []


def test_numeric_statistics_only_numeric_columns():
    df = pd.DataFrame({"amount": [10, 20, 30], "name": ["a", "b", "c"]})
    stats = numeric_statistics(df, detect_column_types(df))
    assert "amount" in stats.columns
    assert "name" not in stats.columns


def test_numeric_statistics_no_numeric_columns():
    df = pd.DataFrame({"name": ["a", "b"]})
    assert numeric_statistics(df, detect_column_types(df)).empty
