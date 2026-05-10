import streamlit as st
import pandas as pd
import zipfile
import sqlite3
import os
import tempfile

st.set_page_config(page_title="Wearable Analytics", layout="wide")

st.title("Wearable Analytics Dashboard")

uploaded_file = st.file_uploader(
    "Upload wearable export ZIP",
    type=["zip"]
)

if uploaded_file is not None:

    st.success("ZIP uploaded successfully!")

    temp_dir = tempfile.mkdtemp()

    zip_path = os.path.join(temp_dir, uploaded_file.name)

    with open(zip_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    extracted_files = []

    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            extracted_files.append(os.path.join(root, file))

    st.subheader("Detected Files")
    st.write(extracted_files)

    # Detect export type
    export_type = "Unknown"

    for file in extracted_files:

        lower = file.lower()

        if "healthconnect" in lower or lower.endswith(".db"):
            export_type = "Health Connect"

        elif "ring_data" in lower:
            export_type = "Ultrahuman"

        elif "zepp" in lower or "activity" in lower:
            export_type = "Zepp"

    st.header(f"Detected Export: {export_type}")

    # HEALTH CONNECT ANALYSIS
    if export_type == "Health Connect":

        db_files = [f for f in extracted_files if f.endswith(".db")]

        if db_files:

            db_path = db_files[0]

            conn = sqlite3.connect(db_path)

            tables = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table';",
                conn
            )

            st.subheader("Database Tables")
            st.dataframe(tables)

            conn.close()
# ULTRAHUMAN ANALYSIS
elif export_type == "Ultrahuman":

    csv_files = [
        f for f in extracted_files
        if f.endswith(".csv")
        and "ring_data" in os.path.basename(f)
    ]

    st.subheader("Detected Ring Data Files")
    st.write(csv_files)

    combined_df = pd.DataFrame()

    # Load all weekly files
    for csv_file in csv_files:

        try:
            df = pd.read_csv(csv_file)

            df["source_file"] = os.path.basename(csv_file)

            combined_df = pd.concat(
                [combined_df, df],
                ignore_index=True
            )

        except Exception as e:

            st.error(f"Failed to read {csv_file}")
            st.error(str(e))

    st.header("Combined Dataset Overview")

    st.write(f"Total Rows: {len(combined_df)}")

    st.subheader("Columns")
    st.write(combined_df.columns.tolist())

    st.subheader("Sample Data")
    st.dataframe(combined_df.head())

    # Detect metric column
    metric_col = None

    for possible_col in [
        "data_type",
        "metric",
        "type"
    ]:

        if possible_col in combined_df.columns:
            metric_col = possible_col
            break

    if metric_col:

        st.header("Detected Metrics")

        metrics = (
            combined_df[metric_col]
            .dropna()
            .unique()
            .tolist()
        )

        st.write(metrics)

        # Metric frequency
        metric_counts = (
            combined_df[metric_col]
            .value_counts()
            .reset_index()
        )

        metric_counts.columns = ["Metric", "Count"]

        st.subheader("Metric Counts")

        st.dataframe(metric_counts)

    else:

        st.warning(
            "No metric column detected."
        )

        csv_files = [f for f in extracted_files if f.endswith(".csv")]

        st.subheader("CSV Files")
        st.write(csv_files)
