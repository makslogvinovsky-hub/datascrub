"""Chart rendering helpers: numeric distribution, top categories, and date
trend. Large datasets are sampled before plotting; callers should still use
the full DataFrame for quality checks, cleaning, and export."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import DEFAULT_SAMPLE_SIZE, LARGE_DATASET_THRESHOLD, get_sample

TOP_N_CATEGORIES = 10


def _sample_for_chart(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) > LARGE_DATASET_THRESHOLD:
        return get_sample(df, max_rows=DEFAULT_SAMPLE_SIZE)
    return df


def render_distribution_chart(df: pd.DataFrame, column: str) -> None:
    """Render a histogram for a numeric column."""
    sample = _sample_for_chart(df)
    values = pd.to_numeric(sample[column], errors="coerce").dropna()
    if values.empty:
        st.info(f"No numeric data available in '{column}' to plot.")
        return
    fig = px.histogram(x=values, nbins=30, labels={"x": column}, title=f"Distribution of {column}")
    st.plotly_chart(fig, use_container_width=True)


def render_top_categories_chart(df: pd.DataFrame, column: str, top_n: int = TOP_N_CATEGORIES) -> None:
    """Render a bar chart of the top N most frequent values in a categorical column."""
    sample = _sample_for_chart(df)
    counts = sample[column].dropna().astype(str).value_counts().head(top_n)
    if counts.empty:
        st.info(f"No data available in '{column}' to plot.")
        return
    st.bar_chart(counts)


def render_date_trend_chart(df: pd.DataFrame, date_column: str, value_column: str = None) -> None:
    """Render a monthly trend line: row counts, or the sum of value_column if given."""
    sample = _sample_for_chart(df)
    dates = pd.to_datetime(sample[date_column], errors="coerce")
    valid = dates.notna()
    if not valid.any():
        st.info(f"No valid dates found in '{date_column}'.")
        return

    if value_column:
        values = pd.to_numeric(sample.loc[valid, value_column], errors="coerce")
        trend = pd.DataFrame({"date": dates[valid], "value": values})
        series = trend.set_index("date")["value"].resample("ME").sum()
    else:
        trend = pd.DataFrame({"date": dates[valid]})
        series = trend.set_index("date").resample("ME").size()

    st.line_chart(series)
