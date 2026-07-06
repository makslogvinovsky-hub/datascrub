"""Tests for src/data_loader.py: delimiter detection, encoding detection, and
loading behavior, including regressions against real messy fixture files."""

import io
from pathlib import Path

import pandas as pd

from src.data_loader import get_excel_sheet_names, load_file

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class FakeUpload(io.BytesIO):
    def __init__(self, data: bytes, name: str):
        super().__init__(data)
        self.name = name


def _load_fixture(filename: str) -> pd.DataFrame:
    raw_bytes = (FIXTURES_DIR / filename).read_bytes()
    return load_file(FakeUpload(raw_bytes, filename))


def test_plain_comma_csv_still_works():
    content = "a,b,c\n1,2,3\n4,5,6\n"
    df = load_file(FakeUpload(content.encode("utf-8"), "comma.csv"))
    assert df.shape == (2, 3)
    assert list(df.columns) == ["a", "b", "c"]


def test_tab_delimited_csv_detected():
    content = "a\tb\tc\n1\t2\t3\n4\t5\t6\n"
    df = load_file(FakeUpload(content.encode("utf-8"), "tab.csv"))
    assert df.shape == (2, 3)


def test_semicolon_delimiter_not_fooled_by_decimal_commas():
    content = "name;city;amount\nAlice;Paris;1 250,50\nBob;Berlin;980,00\n"
    df = load_file(FakeUpload(content.encode("utf-8"), "semicolon.csv"))
    assert df.shape == (2, 3)
    assert list(df.columns) == ["name", "city", "amount"]
    assert df.loc[0, "amount"] == "1 250,50"


def test_polish_cp1250_semicolon_fixture():
    df = _load_fixture("04_polish_cp1250.csv")
    assert df.shape[1] == 4
    assert list(df.columns) == ["Nazwa firmy", "Miasto", "Cena (zł)", "Uwagi"]


def test_polish_cp1250_fixture_has_no_false_duplicates():
    from src.data_profiler import duplicate_summary

    df = _load_fixture("04_polish_cp1250.csv")
    result = duplicate_summary(df)
    assert result["duplicate_count"] == 0


def test_cyrillic_cp1251_fixture():
    df = _load_fixture("05_cyrillic_cp1251.csv")
    assert df.shape[1] == 4
    assert list(df.columns) == ["Наименование", "Поставщик", "Цена", "Количество"]


def test_empty_csv_returns_empty_dataframe():
    df = load_file(FakeUpload(b"", "empty.csv"))
    assert df.shape == (0, 0)


def test_header_only_csv_returns_zero_rows():
    df = load_file(FakeUpload("a,b\n".encode("utf-8"), "headers.csv"))
    assert df.shape == (0, 2)


def _build_multi_sheet_xlsx() -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"a": [1, 2]}).to_excel(writer, sheet_name="First", index=False)
        pd.DataFrame({"b": [3, 4, 5]}).to_excel(writer, sheet_name="Second", index=False)
    return buffer.getvalue()


def test_get_excel_sheet_names_returns_none_for_csv():
    df_upload = FakeUpload(b"a,b\n1,2\n", "plain.csv")
    assert get_excel_sheet_names(df_upload) is None


def test_get_excel_sheet_names_lists_all_sheets():
    upload = FakeUpload(_build_multi_sheet_xlsx(), "multi.xlsx")
    assert get_excel_sheet_names(upload) == ["First", "Second"]


def test_load_file_defaults_to_first_sheet():
    upload = FakeUpload(_build_multi_sheet_xlsx(), "multi.xlsx")
    df = load_file(upload)
    assert list(df.columns) == ["a"]
    assert df.shape == (2, 1)


def test_load_file_selects_requested_sheet():
    upload = FakeUpload(_build_multi_sheet_xlsx(), "multi.xlsx")
    df = load_file(upload, sheet_name="Second")
    assert list(df.columns) == ["b"]
    assert df.shape == (3, 1)
