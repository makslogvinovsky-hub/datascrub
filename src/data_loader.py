"""Load uploaded CSV/XLSX files into DataFrames, with delimiter and encoding
detection for CSV, and a sampling helper for large datasets."""

import io
import re

import pandas as pd
from charset_normalizer import from_bytes

LARGE_DATASET_THRESHOLD = 50_000
DEFAULT_SAMPLE_SIZE = 5_000

CSV_DELIMITER_CANDIDATES = [",", ";", "\t"]
DECIMAL_COMMA_PATTERN = re.compile(r"(?<=\d),(?=\d)")

# Candidates are intentionally narrow (not charset-normalizer's full codepage
# list): 8-bit codepages like cp1250/cp1251/latin1 almost never raise on
# decode, and a broader candidate set (e.g. cp1252) can win on generic
# letter-frequency grounds while still misrendering the specific accented
# characters (e.g. Polish "ł") this app needs to get right.
ENCODING_CANDIDATES = ["utf_8", "cp1250", "cp1251", "iso-8859-1"]


def load_file(uploaded_file, sheet_name: str | None = None) -> pd.DataFrame:
    """Load an uploaded .csv or .xlsx file into a DataFrame. Column names are
    stripped of surrounding whitespace. Returns an empty DataFrame if the
    file has no readable content. `sheet_name` selects a sheet for .xlsx
    files; ignored for .csv. If None, the first sheet is used."""
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        df = _load_csv(uploaded_file)
    elif name.endswith(".xlsx"):
        df = _load_excel(uploaded_file, sheet_name)
    else:
        raise ValueError(f"Unsupported file type: {uploaded_file.name}. Only .csv and .xlsx are supported.")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def get_excel_sheet_names(uploaded_file) -> list[str] | None:
    """Return the sheet names of an uploaded .xlsx file, or None if the file
    is not an .xlsx (e.g. a .csv)."""
    if not uploaded_file.name.lower().endswith(".xlsx"):
        return None
    uploaded_file.seek(0)
    with pd.ExcelFile(uploaded_file, engine="openpyxl") as excel_file:
        return excel_file.sheet_names


def _load_csv(uploaded_file) -> pd.DataFrame:
    uploaded_file.seek(0)
    raw_bytes = uploaded_file.read()
    if not raw_bytes:
        return pd.DataFrame()

    delimiter = _detect_delimiter(raw_bytes)
    encoding = _detect_encoding(raw_bytes)

    try:
        return pd.read_csv(io.BytesIO(raw_bytes), sep=delimiter, encoding=encoding)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    except UnicodeDecodeError as e:
        raise ValueError(f"Could not decode CSV file with any supported encoding ({e}).")


def _count_delimiter(line: str, delimiter: str) -> int:
    if delimiter == ",":
        line = DECIMAL_COMMA_PATTERN.sub("", line)
    return line.count(delimiter)


def _detect_delimiter(raw_bytes: bytes) -> str:
    """Pick the delimiter whose occurrence count is consistent across sample
    lines, preferring the one that yields the most columns. Decimal commas
    (digit,digit) are excluded from the comma count so they can't be mistaken
    for the field separator. Decoded as latin1 for this purpose only, since
    ASCII delimiter bytes are identical across all candidate encodings."""
    sample_text = raw_bytes[:8192].decode("latin1", errors="ignore")
    lines = [line for line in sample_text.splitlines() if line.strip()][:20]
    if not lines:
        return ","

    best_delimiter = ","
    best_field_count = 1
    for delimiter in CSV_DELIMITER_CANDIDATES:
        counts = [_count_delimiter(line, delimiter) for line in lines]
        if counts[0] == 0 or len(set(counts)) != 1:
            continue
        field_count = counts[0] + 1
        if field_count > best_field_count:
            best_field_count = field_count
            best_delimiter = delimiter
    return best_delimiter


def _detect_encoding(raw_bytes: bytes) -> str:
    """Detect the CSV's encoding via content-aware scoring (charset-normalizer),
    restricted to our supported candidates. "First encoding that doesn't raise"
    is not reliable here: 8-bit codepages like cp1250/cp1251/latin1 decode
    almost any byte sequence without error, so a cp1251 file can "successfully"
    decode as cp1250 and silently produce mojibake."""
    match = from_bytes(raw_bytes, cp_isolation=ENCODING_CANDIDATES).best()
    if match is None:
        return "utf-8"
    return match.encoding


def _load_excel(uploaded_file, sheet_name: str | None = None) -> pd.DataFrame:
    uploaded_file.seek(0)
    try:
        return pd.read_excel(uploaded_file, sheet_name=sheet_name or 0, engine="openpyxl")
    except ValueError:
        return pd.DataFrame()


def get_sample(df: pd.DataFrame, max_rows: int = DEFAULT_SAMPLE_SIZE) -> pd.DataFrame:
    """Return a random sample of df when it exceeds max_rows, otherwise df itself.
    Used for preview/chart rendering only — quality checks, cleaning, and export
    always use the full DataFrame."""
    if len(df) > max_rows:
        return df.sample(n=max_rows, random_state=42)
    return df
