import pandas as pd
import streamlit as st

from src.charts import (
    render_date_trend_chart,
    render_distribution_chart,
    render_top_categories_chart,
)
from src.cleaner import MISSING_VALUE_STRATEGIES, clean_data
from src.data_loader import load_file
from src.data_profiler import (
    CATEGORICAL,
    DATETIME,
    NUMERIC,
    detect_column_types,
    duplicate_summary,
    missing_value_summary,
    numeric_statistics,
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

    st.subheader("Data Cleaning")
    remove_duplicates = st.checkbox("Remove duplicate rows", value=True)
    missing_strategy = st.selectbox("Missing value strategy", MISSING_VALUE_STRATEGIES)

    cleaned_df, clean_summary = clean_data(df, remove_duplicates, missing_strategy)

    st.markdown(
        f"**Rows:** {clean_summary['rows_before']} → {clean_summary['rows_after']}  \n"
        f"**Duplicates removed:** {clean_summary['duplicates_removed']}  \n"
        f"**Rows dropped (missing values):** {clean_summary['rows_dropped_missing']}  \n"
        f"**Cells filled:** {clean_summary['cells_filled']}"
    )

    st.markdown("**Cleaned data preview**")
    st.dataframe(cleaned_df.head(20), use_container_width=True)

    st.download_button(
        "Download cleaned data (CSV)",
        data=cleaned_df.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_data.csv",
        mime="text/csv",
    )

    st.subheader("Basic Statistics")
    cleaned_column_types = detect_column_types(cleaned_df)
    stats_df = numeric_statistics(cleaned_df, cleaned_column_types)
    if stats_df.empty:
        st.info("No numeric columns available for statistics.")
    else:
        st.dataframe(stats_df, use_container_width=True)

    st.subheader("Charts")
    numeric_cols = [c for c, t in cleaned_column_types.items() if t == NUMERIC]
    categorical_cols = [c for c, t in cleaned_column_types.items() if t == CATEGORICAL]
    datetime_cols = [c for c, t in cleaned_column_types.items() if t == DATETIME]

    if numeric_cols:
        st.markdown("**Numeric Distribution**")
        dist_col = st.selectbox("Column", numeric_cols, key="dist_col")
        render_distribution_chart(cleaned_df, dist_col)

    if categorical_cols:
        st.markdown("**Top Categories**")
        cat_col = st.selectbox("Column", categorical_cols, key="cat_col")
        render_top_categories_chart(cleaned_df, cat_col)

    if datetime_cols:
        st.markdown("**Date Trend**")
        date_col = st.selectbox("Date column", datetime_cols, key="date_col")
        value_choice = st.selectbox("Value to aggregate", ["Row count"] + numeric_cols, key="date_value_col")
        render_date_trend_chart(cleaned_df, date_col, None if value_choice == "Row count" else value_choice)

    if not numeric_cols and not categorical_cols and not datetime_cols:
        st.info("No columns available to chart.")
