import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import zipfile
import io

# =====================================================
# PAGE CONFIG
# =====================================================

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

                df = load_csv_from_zip(z, file)

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
            # NUMERIC COLUMNS
            # =========================================

            numeric_cols = combined_df.select_dtypes(
                include=np.number
            ).columns.tolist()

            st.subheader("Numeric Metrics")

            st.write(numeric_cols)

            # =========================================
            # DATE DETECTION
            # =========================================

            possible_dates = [
                c for c in combined_df.columns
                if "date" in c.lower()
                or "time" in c.lower()
            ]

            # Ultrahuman epoch conversion
            if "timestamp_epoch" in combined_df.columns:

                combined_df["datetime"] = pd.to_datetime(
                    combined_df["timestamp_epoch"],
                    unit="s",
                    errors="coerce"
                )

                possible_dates.append("datetime")

            st.subheader("Possible Date Columns")

            st.write(possible_dates)

            # =========================================
            # DATA TYPES
            # =========================================

            if "data_type" in combined_df.columns:

                st.subheader("Detected Data Types")

                data_types = (
                    combined_df["data_type"]
                    .value_counts()
                    .reset_index()
                )

                data_types.columns = [
                    "data_type",
                    "count"
                ]

                st.dataframe(data_types)

                selected_type = st.selectbox(
                    "Select Metric",
                    data_types["data_type"].tolist()
                )

                filtered = combined_df[
                    combined_df["data_type"] == selected_type
                ]

            else:

                filtered = combined_df.copy()

            # =========================================
            # VISUALIZATION
            # =========================================

            if (
                len(possible_dates) > 0
                and len(numeric_cols) > 0
            ):

                if "datetime" in filtered.columns:
                    date_col = "datetime"
                else:
                    date_col = possible_dates[0]

                metric_col = "value"

                filtered = filtered.dropna(
                    subset=[date_col]
                )

                filtered["date"] = (
                    filtered[date_col].dt.date
                )

                daily = (
                    filtered.groupby("date")[metric_col]
                    .mean()
                    .reset_index()
                )

                st.subheader(
                    f"{selected_type} Trend"
                )

                fig = px.line(
                    daily,
                    x="date",
                    y=metric_col,
                    title=f"{selected_type} Over Time"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                # =====================================
                # SUMMARY STATS
                # =====================================

                st.subheader("Summary Statistics")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Average",
                        f"{daily[metric_col].mean():.2f}"
                    )

                with col2:
                    st.metric(
                        "Maximum",
                        f"{daily[metric_col].max():.2f}"
                    )

                with col3:
                    st.metric(
                        "Minimum",
                        f"{daily[metric_col].min():.2f}"
                    )

                # =====================================
                # RAW DATA
                # =====================================

                with st.expander("View Raw Data"):

                    st.dataframe(filtered.head(1000))

else:

    st.info(
        "Upload your wearable ZIP export."
    )
