import pandas as pd
import streamlit as st

from src.data_loader import load_file
from src.data_profiler import (
    detect_column_types,
    duplicate_summary,
    missing_value_summary,
    quality_warnings,
    total_missing,
)

st.set_page_config(page_title="DataScrub", page_icon="🧹", layout="wide")

st.title("🧹 DataScrub")
st.caption("Upload messy Excel — get clean data and instant insights.")

uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx"])

if uploaded_file is None:
    st.info("Upload a .csv or .xlsx file to get started.")
else:
    try:
        df = load_file(uploaded_file)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    if df.shape[1] == 0:
        st.warning("The uploaded file appears to be empty.")
        st.stop()

    st.subheader("Dataset Overview")
    col1, col2 = st.columns(2)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])

    st.subheader("Preview")
    if df.empty:
        st.info("The file has column headers but no data rows.")
    else:
        st.dataframe(df.head(20), use_container_width=True)

    column_types = detect_column_types(df)

    st.subheader("Detected Column Types")
    types_df = pd.DataFrame({
        "Column": list(column_types.keys()),
        "Detected Type": list(column_types.values()),
    })
    st.dataframe(types_df, use_container_width=True)

    st.subheader("Data Quality Summary")
    dup_info = duplicate_summary(df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Missing Values", total_missing(df))
    col2.metric("Duplicate Rows", dup_info["duplicate_count"])
    col3.metric("Duplicate %", f"{dup_info['duplicate_percentage']}%")

    st.markdown("**Missing values by column**")
    st.dataframe(missing_value_summary(df), use_container_width=True)

    warnings = quality_warnings(df, column_types)
    if warnings:
        st.markdown("**Warnings**")
        for warning in warnings:
            st.warning(warning)
