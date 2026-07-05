"""Column type detection and data-quality summaries (missing values, duplicates,
basic warnings)."""

import pandas as pd

NUMERIC = "numeric"
CATEGORICAL = "categorical"
DATETIME = "datetime"
MIXED = "mixed/unknown"

PARSE_SUCCESS_THRESHOLD = 0.9
MIXED_LOWER_THRESHOLD = 0.2
CONSTANT_COLUMN_WARNING_MIN_ROWS = 2
HIGH_MISSING_WARNING_PCT = 50


def detect_column_types(df: pd.DataFrame) -> dict:
    """Classify each column as numeric, datetime, categorical, or mixed/unknown."""
    return {col: _detect_type(df[col]) for col in df.columns}


def _detect_type(series: pd.Series) -> str:
    non_null = series.dropna()
    if non_null.empty:
        return MIXED

    if pd.api.types.is_numeric_dtype(series):
        return NUMERIC
    if pd.api.types.is_datetime64_any_dtype(series):
        return DATETIME

    numeric_ratio = pd.to_numeric(non_null, errors="coerce").notna().mean()
    if numeric_ratio >= PARSE_SUCCESS_THRESHOLD:
        return NUMERIC

    datetime_ratio = pd.to_datetime(non_null, errors="coerce", format="mixed").notna().mean()
    if datetime_ratio >= PARSE_SUCCESS_THRESHOLD:
        return DATETIME

    if MIXED_LOWER_THRESHOLD <= max(numeric_ratio, datetime_ratio) < PARSE_SUCCESS_THRESHOLD:
        return MIXED

    return CATEGORICAL


def missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-column missing value count and percentage."""
    if df.shape[1] == 0:
        return pd.DataFrame(columns=["Column", "Missing Count", "Missing %"])
    total_rows = len(df)
    counts = df.isna().sum()
    pct = (counts / total_rows * 100).round(1) if total_rows > 0 else counts.astype(float)
    return pd.DataFrame({
        "Column": df.columns,
        "Missing Count": counts.values,
        "Missing %": pct.values,
    })


def total_missing(df: pd.DataFrame) -> int:
    """Total number of missing cells across the whole DataFrame."""
    return int(df.isna().sum().sum())


def duplicate_summary(df: pd.DataFrame) -> dict:
    """Duplicate row count and percentage of total rows."""
    total_rows = len(df)
    if total_rows == 0:
        return {"duplicate_count": 0, "duplicate_percentage": 0.0}
    dup_count = int(df.duplicated().sum())
    return {
        "duplicate_count": dup_count,
        "duplicate_percentage": round(dup_count / total_rows * 100, 1),
    }


def quality_warnings(df: pd.DataFrame, column_types: dict) -> list:
    """Simple, human-readable warnings about problematic columns."""
    warnings = []
    if len(df) == 0:
        return warnings
    for col in df.columns:
        missing_pct = df[col].isna().mean() * 100
        if missing_pct >= HIGH_MISSING_WARNING_PCT:
            warnings.append(f"Column '{col}' has {missing_pct:.0f}% missing values.")
        if column_types.get(col) == MIXED:
            warnings.append(f"Column '{col}' has mixed/inconsistent data types.")
        if len(df) >= CONSTANT_COLUMN_WARNING_MIN_ROWS and df[col].nunique(dropna=True) <= 1:
            warnings.append(f"Column '{col}' has a single constant value.")
    return warnings
