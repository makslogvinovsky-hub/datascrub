"""Load uploaded CSV/XLSX files into DataFrames, with encoding fallback for CSV
and a sampling helper for large datasets."""

import pandas as pd

CSV_ENCODINGS = ["utf-8-sig", "utf-8", "cp1250", "cp1251", "latin1"]
LARGE_DATASET_THRESHOLD = 50_000
DEFAULT_SAMPLE_SIZE = 5_000


def load_file(uploaded_file) -> pd.DataFrame:
    """Load an uploaded .csv or .xlsx file into a DataFrame. Column names are
    stripped of surrounding whitespace. Returns an empty DataFrame if the
    file has no readable content."""
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        df = _load_csv(uploaded_file)
    elif name.endswith(".xlsx"):
        df = _load_excel(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {uploaded_file.name}. Only .csv and .xlsx are supported.")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _load_csv(uploaded_file) -> pd.DataFrame:
    last_error = None
    for encoding in CSV_ENCODINGS:
        try:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding=encoding)
        except UnicodeDecodeError as e:
            last_error = e
            continue
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
    raise ValueError(f"Could not decode CSV file with any supported encoding ({last_error}).")


def _load_excel(uploaded_file) -> pd.DataFrame:
    try:
        return pd.read_excel(uploaded_file, engine="openpyxl")
    except ValueError:
        return pd.DataFrame()


def get_sample(df: pd.DataFrame, max_rows: int = DEFAULT_SAMPLE_SIZE) -> pd.DataFrame:
    """Return a random sample of df when it exceeds max_rows, otherwise df itself.
    Used for preview/chart rendering only — quality checks, cleaning, and export
    always use the full DataFrame."""
    if len(df) > max_rows:
        return df.sample(n=max_rows, random_state=42)
    return df
