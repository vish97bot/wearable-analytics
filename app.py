import streamlit as st
import pandas as pd
import zipfile
import os
import tempfile

st.set_page_config(
    page_title="Wearable Analytics",
    layout="wide"
)

st.title("Wearable Analytics Dashboard")

uploaded_file = st.file_uploader(
    "Upload Ultrahuman ZIP",
    type=["zip"]
)

if uploaded_file is not None:

    st.success("ZIP uploaded!")

    # Create temp directory
    temp_dir = tempfile.mkdtemp()

    zip_path = os.path.join(
        temp_dir,
        uploaded_file.name
    )

    # Save ZIP
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract ZIP
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Collect files
    extracted_files = []

    for root, dirs, files in os.walk(temp_dir):

        for file in files:

            full_path = os.path.join(root, file)

            extracted_files.append(full_path)

    st.header("Extracted Files")

    st.write(extracted_files)

    # Find ring data CSVs
    ring_csvs = []

    for file in extracted_files:

        filename = os.path.basename(file)

        if (
            filename.endswith(".csv")
            and "ring_data" in filename
        ):

            ring_csvs.append(file)

    st.header("Ring CSV Files")

    st.write(ring_csvs)

    # Read first CSV only
    if len(ring_csvs) > 0:

        first_csv = ring_csvs[0]

        st.header("Reading First CSV")

        st.write(first_csv)

        try:

            df = pd.read_csv(first_csv)

            st.success("CSV loaded successfully!")

            st.header("Columns")

            st.write(df.columns.tolist())

            st.header("Shape")

            st.write(df.shape)

            st.header("Sample Data")

            st.dataframe(df.head())

        except Exception as e:

            st.error("CSV failed to load")

            st.error(str(e))
