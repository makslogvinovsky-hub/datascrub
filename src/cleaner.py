"""Data cleaning operations: text normalization, duplicate removal, and
missing-value handling, with a transparent summary of what changed."""

import pandas as pd

from src.data_profiler import CATEGORICAL, NUMERIC, detect_column_types

STRATEGY_LEAVE = "Leave as is"
STRATEGY_DROP = "Drop rows with missing values"
STRATEGY_FILL = 'Fill missing (median for numeric, "Unknown" for text)'

MISSING_VALUE_STRATEGIES = [STRATEGY_LEAVE, STRATEGY_DROP, STRATEGY_FILL]


def _normalize_text_value(value):
    if pd.isna(value):
        return value
    return str(value).strip().title()


def clean_data(
    df: pd.DataFrame,
    remove_duplicates: bool,
    missing_strategy: str,
    normalize_text: bool = False,
) -> tuple:
    """Apply the selected cleaning steps to df and return (cleaned_df, summary).

    summary keys: rows_before, rows_after, duplicates_removed, rows_dropped_missing,
    cells_filled, normalized_cells.
    """
    cleaned = df.copy()
    rows_before = len(cleaned)
    column_types = detect_column_types(cleaned)

    normalized_cells = 0
    if normalize_text:
        for col, col_type in column_types.items():
            if col_type != CATEGORICAL:
                continue
            original = cleaned[col]
            normalized = original.map(_normalize_text_value)
            changed = original.notna() & (original != normalized)
            normalized_cells += int(changed.sum())
            cleaned[col] = normalized

    duplicates_removed = 0
    if remove_duplicates:
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates()
        duplicates_removed = before - len(cleaned)

    rows_dropped = 0
    cells_filled = 0
    if missing_strategy == STRATEGY_DROP:
        before = len(cleaned)
        cleaned = cleaned.dropna()
        rows_dropped = before - len(cleaned)
    elif missing_strategy == STRATEGY_FILL:
        cells_filled = int(cleaned.isna().sum().sum())
        for col in cleaned.columns:
            if not cleaned[col].isna().any():
                continue
            if column_types.get(col) == NUMERIC:
                median = pd.to_numeric(cleaned[col], errors="coerce").median()
                cleaned[col] = cleaned[col].fillna(median)
            else:
                cleaned[col] = cleaned[col].fillna("Unknown")

    summary = {
        "rows_before": rows_before,
        "rows_after": len(cleaned),
        "duplicates_removed": duplicates_removed,
        "rows_dropped_missing": rows_dropped,
        "cells_filled": cells_filled,
        "normalized_cells": normalized_cells,
    }
    return cleaned.reset_index(drop=True), summary
