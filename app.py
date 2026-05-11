import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import zipfile
import io

st.set_page_config(
    page_title="Wearable Intelligence Dashboard",
    layout="wide"
)

# =========================
# CUSTOM STYLING
# =========================

st.markdown("""
<style>

.main {
    background-color: #0f172a;
}

.metric-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 20px;
    border: 1px solid #1f2937;
    text-align: center;
}

.metric-title {
    color: #9ca3af;
    font-size: 14px;
}

.metric-value {
    color: white;
    font-size: 40px;
    font-weight: bold;
}

.section-title {
    font-size: 28px;
    font-weight: bold;
    margin-top: 10px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================

st.title("Wearable Intelligence Dashboard")
st.caption("Ultrahuman • Zepp • Health Connect")

# =========================
# SIDEBAR
# =========================

st.sidebar.header("Controls")

uploaded_zip = st.sidebar.file_uploader(
    "Upload Wearable ZIP",
    type=["zip"]
)

selected_days = st.sidebar.slider(
    "Days to Display",
    min_value=7,
    max_value=365,
    value=60
)

show_raw = st.sidebar.checkbox("Show Raw Data")

# =========================
# HELPERS
# =========================

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

# =========================
# MAIN
# =========================

if uploaded_zip is not None:

    zip_bytes = io.BytesIO(uploaded_zip.read())

    with zipfile.ZipFile(zip_bytes) as z:

        files = z.namelist()

        ring_files = [
            f for f in files
            if "ring_data" in f.lower()
            and f.endswith(".csv")
        ]

        combined_df = pd.DataFrame()

        progress = st.progress(0)

        for i, file in enumerate(ring_files):

            try:

                df = load_csv_from_zip(z, file)

                df["source_file"] = file

                combined_df = pd.concat(
                    [combined_df, df],
                    ignore_index=True
                )

            except Exception:
                pass

            progress.progress((i + 1) / len(ring_files))

        # =========================
        # PROCESSING
        # =========================

        if not combined_df.empty:

            if "timestamp_epoch" in combined_df.columns:

                combined_df["datetime"] = pd.to_datetime(
                    combined_df["timestamp_epoch"],
                    unit="s",
                    errors="coerce"
                )

                combined_df["date"] = (
                    combined_df["datetime"].dt.date
                )

            combined_df = combined_df.dropna(
                subset=["date"]
            )

            latest_date = pd.to_datetime(
                combined_df["date"]
            ).max()

            cutoff_date = latest_date - pd.Timedelta(
                days=selected_days
            )

            combined_df = combined_df[
                pd.to_datetime(combined_df["date"])
                >= cutoff_date
            ]

            # =========================
            # HRV DATA
            # =========================

            hrv_df = combined_df[
                combined_df["data_type"] == "raw_hrv_2"
            ].copy()

            recovery_score = 0
            avg_hrv = 0

            if not hrv_df.empty:

                daily_hrv = (
                    hrv_df.groupby("date")["value"]
                    .mean()
                    .reset_index()
                )

                avg_hrv = daily_hrv["value"].tail(7).mean()

                recovery_score = np.clip(
                    (avg_hrv / 120) * 100,
                    0,
                    100
                )

            sleep_score = np.clip(
                recovery_score * 0.92,
                0,
                100
            )

            readiness_score = (
                recovery_score * 0.6 +
                sleep_score * 0.4
            )

            # =========================
            # HERO METRICS
            # =========================

            st.markdown(
                '<div class="section-title">Overview</div>',
                unsafe_allow_html=True
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Recovery</div>
                    <div class="metric-value">{recovery_score:.0f}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Sleep</div>
                    <div class="metric-value">{sleep_score:.0f}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Readiness</div>
                    <div class="metric-value">{readiness_score:.0f}</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Average HRV</div>
                    <div class="metric-value">{avg_hrv:.0f}</div>
                </div>
                """, unsafe_allow_html=True)

            # =========================
            # TABS
            # =========================

            tab1, tab2, tab3, tab4 = st.tabs([
                "Overview",
                "Recovery",
                "Trends",
                "Insights"
            ])

            # =========================
            # TAB 1
            # =========================

            with tab1:

                st.subheader("HRV Trend")

                if not hrv_df.empty:

                    fig = px.line(
                        daily_hrv,
                        x="date",
                        y="value",
                        title="Daily HRV"
                    )

                    fig.update_layout(
                        template="plotly_dark",
                        height=450
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

            # =========================
            # TAB 2
            # =========================

            with tab2:

                if not hrv_df.empty:

                    recovery_df = daily_hrv.copy()

                    recovery_df["rolling_hrv"] = (
                        recovery_df["value"]
                        .rolling(7)
                        .mean()
                    )

                    fig = px.line(
                        recovery_df,
                        x="date",
                        y=["value", "rolling_hrv"],
                        title="Recovery Trend"
                    )

                    fig.update_layout(
                        template="plotly_dark",
                        height=500
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

            # =========================
            # TAB 3
            # =========================

            with tab3:

                if not hrv_df.empty:

                    fig = px.histogram(
                        hrv_df,
                        x="value",
                        nbins=50,
                        title="HRV Distribution"
                    )

                    fig.update_layout(
                        template="plotly_dark",
                        height=450
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

            # =========================
            # TAB 4
            # =========================

            with tab4:

                st.subheader("AI Insights")

                insights = []

                if avg_hrv > 90:
                    insights.append(
                        "Recovery appears strong with elevated HRV."
                    )

                if avg_hrv < 50:
                    insights.append(
                        "HRV appears suppressed which may indicate fatigue."
                    )

                if recovery_score > 80:
                    insights.append(
                        "Current recovery trend suggests good readiness."
                    )

                if recovery_score < 60:
                    insights.append(
                        "Recovery score is trending lower than ideal."
                    )

                if len(insights) == 0:
                    insights.append(
                        "Not enough data for advanced insights yet."
                    )

                for insight in insights:
                    st.info(insight)

            # =========================
            # RAW DATA
            # =========================

            if show_raw:

                st.subheader("Raw Dataset")

                st.dataframe(
                    combined_df.head(1000)
                )

else:

    st.info(
        "Upload your wearable ZIP export to begin analysis."
    )
