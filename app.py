import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import zipfile
import io

st.set_page_config(
    page_title="Wearable Analytics Dashboard",
    layout="wide"
)

st.title("Personal Wearable Analytics Dashboard")

st.caption(
    "Upload Zepp, Ultrahuman, or Health Connect exports"
)

# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_zip = st.file_uploader(
    "Upload ZIP Export",
    type=["zip"]
)

# =====================================================
# HELPERS
# =====================================================

def find_csv(zip_file, keyword):

    for file in zip_file.namelist():

        if keyword.lower() in file.lower() and file.endswith(".csv"):
            return file

    return None

def load_csv_from_zip(zip_file, filename):

    with zip_file.open(filename) as f:

        try:
            return pd.read_csv(
                f,
                sep=None,
                engine="python",
                on_bad_lines="skip",
                encoding="utf-8"
            )

        except Exception:

            f.seek(0)

            return pd.read_csv(
                f,
                sep=";",
                engine="python",
                on_bad_lines="skip",
                encoding="latin1"
            )


# =====================================================
# MAIN
# =====================================================
if uploaded_zip is not None:

    zip_bytes = io.BytesIO(uploaded_zip.read())

    with zipfile.ZipFile(zip_bytes) as z:

        st.success("ZIP uploaded successfully")

        files = z.namelist()

        st.subheader("Files Detected")

        st.write(files)

        # =============================================
        # FIND RING DATA FILES
        # =============================================

        ring_files = [
            f for f in files
            if "ring_data" in f.lower()
            and f.endswith(".csv")
        ]

        st.subheader("Ring Data Files")

        st.write(f"Detected {len(ring_files)} ring data files")

        # =============================================
        # LOAD ALL RING FILES
        # =============================================

        combined_df = pd.DataFrame()

        for file in ring_files:

            try:

                with z.open(file) as f:

                    df = pd.read_csv(
                        f,
                        sep=None,
                        engine="python",
                        on_bad_lines="skip"
                    )

                    df["source_file"] = file

                    combined_df = pd.concat(
                        [combined_df, df],
                        ignore_index=True
                    )

            except Exception as e:

                st.warning(f"Could not load {file}: {e}")

        # =============================================
        # DISPLAY DATA
        # =============================================

        if not combined_df.empty:

            st.subheader("Combined Ring Dataset")

            st.write(
                f"Total rows loaded: {len(combined_df):,}"
            )

            st.dataframe(combined_df.head())

            st.subheader("Columns")

            st.write(combined_df.columns.tolist())

            # =========================================
            # FIND NUMERIC COLUMNS
            # =========================================

            numeric_cols = combined_df.select_dtypes(
                include=np.number
            ).columns.tolist()

            st.subheader("Numeric Metrics")

            st.write(numeric_cols)

            # =========================================
            # DATE DETECTION
            # =========================================

            possible_dates

        # =================================================
        # LOAD SLEEP
        # =================================================

        sleep_file = find_csv(z, "sleep")

        if sleep_file:

            sleep_df = load_csv_from_zip(z, sleep_file)

            st.subheader("Sleep Data")

            st.dataframe(sleep_df.head())

            cols = sleep_df.columns.tolist()

            st.write("Columns:", cols)

            date_col = None

            for c in cols:
                if "time" in c.lower() or "date" in c.lower():
                    date_col = c
                    break

            if date_col:

                sleep_df[date_col] = pd.to_datetime(
                    sleep_df[date_col],
                    errors="coerce"
                )

                sleep_df["date"] = sleep_df[date_col].dt.date

                numeric_cols = sleep_df.select_dtypes(
                    include=np.number
                ).columns

                if len(numeric_cols) > 0:

                    metric = numeric_cols[0]

                    daily_sleep = (
                        sleep_df.groupby("date")[metric]
                        .mean()
                        .reset_index()
                    )

                    fig = px.line(
                        daily_sleep,
                        x="date",
                        y=metric,
                        title="Sleep Trend"
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

        # =================================================
        # LOAD ACTIVITY
        # =================================================

        activity_file = find_csv(z, "activity")

        if activity_file:

            activity_df = load_csv_from_zip(
                z,
                activity_file
            )

            st.subheader("Activity Data")

            st.dataframe(activity_df.head())

            cols = activity_df.columns.tolist()

            st.write("Columns:", cols)

            numeric_cols = activity_df.select_dtypes(
                include=np.number
            ).columns

            date_col = None

            for c in cols:
                if "time" in c.lower() or "date" in c.lower():
                    date_col = c
                    break

            if date_col and len(numeric_cols) > 0:

                activity_df[date_col] = pd.to_datetime(
                    activity_df[date_col],
                    errors="coerce"
                )

                activity_df["date"] = (
                    activity_df[date_col].dt.date
                )

                metric = numeric_cols[0]

                daily_activity = (
                    activity_df.groupby("date")[metric]
                    .sum()
                    .reset_index()
                )

                fig = px.bar(
                    daily_activity,
                    x="date",
                    y=metric,
                    title="Activity Trend"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        # =================================================
        # HEART RATE
        # =================================================

        hr_file = find_csv(z, "heart")

        if hr_file:

            hr_df = load_csv_from_zip(z, hr_file)

            st.subheader("Heart Rate Data")

            st.dataframe(hr_df.head())

            cols = hr_df.columns.tolist()

            st.write("Columns:", cols)

            numeric_cols = hr_df.select_dtypes(
                include=np.number
            ).columns

            date_col = None

            for c in cols:
                if "time" in c.lower() or "date" in c.lower():
                    date_col = c
                    break

            if date_col and len(numeric_cols) > 0:

                hr_df[date_col] = pd.to_datetime(
                    hr_df[date_col],
                    errors="coerce"
                )

                hr_df["date"] = hr_df[date_col].dt.date

                metric = numeric_cols[0]

                daily_hr = (
                    hr_df.groupby("date")[metric]
                    .mean()
                    .reset_index()
                )

                fig = px.line(
                    daily_hr,
                    x="date",
                    y=metric,
                    title="Heart Rate Trend"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

else:

    st.info(
        "Upload your wearable ZIP export to begin analysis."
    )
