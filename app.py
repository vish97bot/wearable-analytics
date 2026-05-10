import streamlit as st
import pandas as pd
import zipfile
import os

st.set_page_config(page_title="Wearable Analytics", layout="wide")

st.title("Wearable Analytics Dashboard")

uploaded_file = st.file_uploader(
    "Upload your wearable export ZIP",
    type=["zip"]
)

if uploaded_file is not None:

    st.success("File uploaded successfully!")

    zip_path = uploaded_file.name

    with open(zip_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:

        file_list = zip_ref.namelist()

        st.subheader("Files inside ZIP")
        st.write(file_list)

        extract_folder = "extracted_data"

        zip_ref.extractall(extract_folder)

    st.success("ZIP extracted successfully!")
