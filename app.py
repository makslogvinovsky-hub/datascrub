import streamlit as st

from src.data_loader import load_file

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

    st.subheader("Column Types (raw)")
    st.table(df.dtypes.astype(str).rename("Dtype"))
