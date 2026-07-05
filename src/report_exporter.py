"""Build a multi-sheet Excel report: summary, data quality, cleaned data,
and (if numeric columns exist) basic statistics."""

import io

import pandas as pd

from src.data_profiler import duplicate_summary, missing_value_summary, numeric_statistics, total_missing


def build_report(df: pd.DataFrame, cleaned_df: pd.DataFrame, cleaned_column_types: dict) -> bytes:
    """Build an Excel report (as bytes): a Summary sheet and Data Quality sheet
    describing the original upload, a Cleaned Data sheet, and an optional
    Statistics sheet for numeric columns in the cleaned data."""
    dup_info = duplicate_summary(df)
    summary_df = pd.DataFrame({
        "Metric": ["Rows", "Columns", "Total Missing Values", "Duplicate Rows", "Duplicate %"],
        "Value": [
            df.shape[0],
            df.shape[1],
            total_missing(df),
            dup_info["duplicate_count"],
            dup_info["duplicate_percentage"],
        ],
    })
    quality_df = missing_value_summary(df)
    stats_df = numeric_statistics(cleaned_df, cleaned_column_types)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        quality_df.to_excel(writer, sheet_name="Data Quality", index=False)
        cleaned_df.to_excel(writer, sheet_name="Cleaned Data", index=False)
        if not stats_df.empty:
            stats_df.to_excel(writer, sheet_name="Statistics")
    return buffer.getvalue()
