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
# STYLING
# =========================

st.markdown("""
<style>

.metric-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #1f2937;
    text-align: center;
}

.metric-title {
    color: #9ca3af;
    font-size: 14px;
}

.metric-value {
    color: white;
    font-size: 38px;
    font-weight: bold;
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

uploaded_zip = st.sidebar.file_uploader(
    "Upload Wearable ZIP",
    type=["zip"]
)

selected_days = st.sidebar.slider(
    "Days to Display",
    7,
    365,
    60
)

show_raw = st.sidebar.checkbox("Show Raw Data")

# =========================
# HELPERS
# =========================

def load_csv(zip_file, filename):

    with zip_file.open(filename) as f:

        try:

            return pd.read_csv(
                f,
                sep=None,
                engine="python",
                on_bad_lines="skip"
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

        st.sidebar.success(
            f"{len(files)} files detected"
        )

        daily_metrics = pd.DataFrame()

        # =================================================
        # ULTRAHUMAN PARSER
        # =================================================

        ring_files = [
            f for f in files
            if "ring_data" in f.lower()
        ]

        if len(ring_files) > 0:

            combined = pd.DataFrame()

            for file in ring_files:

                try:

                    df = load_csv(z, file)

                    combined = pd.concat(
                        [combined, df],
                        ignore_index=True
                    )

                except Exception:
                    pass

            if not combined.empty:

                if "timestamp_epoch" in combined.columns:

                    combined["datetime"] = pd.to_datetime(
                        combined["timestamp_epoch"],
                        unit="s",
                        errors="coerce"
                    )

                    combined["date"] = (
                        combined["datetime"].dt.date
                    )

                # HRV

                hrv = combined[
                    combined["data_type"] == "raw_hrv_2"
                ]

                if not hrv.empty:

                    daily_hrv = (
                        hrv.groupby("date")["value"]
                        .mean()
                        .reset_index()
                    )

                    daily_hrv.rename(
                        columns={"value": "hrv"},
                        inplace=True
                    )

                    daily_metrics = daily_hrv.copy()

        # =================================================
        # ZEPP PARSER
        # =================================================

        sleep_files = [
            f for f in files
            if "sleep" in f.lower()
            and f.endswith(".csv")
        ]

        hr_files = [
            f for f in files
            if "heartrate" in f.lower()
            and f.endswith(".csv")
        ]

        activity_files = [
            f for f in files
            if "activity" in f.lower()
            and f.endswith(".csv")
        ]

        # SLEEP

        for file in sleep_files:

            try:

                df = load_csv(z, file)

                date_cols = [
                    c for c in df.columns
                    if "time" in c.lower()
                    or "date" in c.lower()
                ]

                if len(date_cols) > 0:

                    date_col = date_cols[0]

                    df[date_col] = pd.to_datetime(
                        df[date_col],
                        errors="coerce"
                    )

                    df["date"] = (
                        df[date_col].dt.date
                    )

                    numeric_cols = df.select_dtypes(
                        include=np.number
                    ).columns

                    if len(numeric_cols) > 0:

                        metric_col = numeric_cols[0]

                        sleep_daily = (
                            df.groupby("date")[metric_col]
                            .mean()
                            .reset_index()
                        )

                        sleep_daily.rename(
                            columns={
                                metric_col: "sleep_metric"
                            },
                            inplace=True
                        )

                        if daily_metrics.empty:

                            daily_metrics = sleep_daily

                        else:

                            daily_metrics = daily_metrics.merge(
                                sleep_daily,
                                on="date",
                                how="outer"
                            )

            except Exception:
                pass

        # HEART RATE

        for file in hr_files:

            try:

                df = load_csv(z, file)

                date_cols = [
                    c for c in df.columns
                    if "time" in c.lower()
                    or "date" in c.lower()
                ]

                if len(date_cols) > 0:

                    date_col = date_cols[0]

                    df[date_col] = pd.to_datetime(
                        df[date_col],
                        errors="coerce"
                    )

                    df["date"] = (
                        df[date_col].dt.date
                    )

                    numeric_cols = df.select_dtypes(
                        include=np.number
                    ).columns

                    if len(numeric_cols) > 0:

                        metric_col = numeric_cols[0]

                        hr_daily = (
                            df.groupby("date")[metric_col]
                            .mean()
                            .reset_index()
                        )

                        hr_daily.rename(
                            columns={
                                metric_col: "heart_rate"
                            },
                            inplace=True
                        )

                        if daily_metrics.empty:

                            daily_metrics = hr_daily

                        else:

                            daily_metrics = daily_metrics.merge(
                                hr_daily,
                                on="date",
                                how="outer"
                            )

            except Exception:
                pass

        # ACTIVITY

        for file in activity_files:

            try:

                df = load_csv(z, file)

                date_cols = [
                    c for c in df.columns
                    if "time" in c.lower()
                    or "date" in c.lower()
                ]

                if len(date_cols) > 0:

                    date_col = date_cols[0]

                    df[date_col] = pd.to_datetime(
                        df[date_col],
                        errors="coerce"
                    )

                    df["date"] = (
                        df[date_col].dt.date
                    )

                    numeric_cols = df.select_dtypes(
                        include=np.number
                    ).columns

                    if len(numeric_cols) > 0:

                        metric_col = numeric_cols[0]

                        activity_daily = (
                            df.groupby("date")[metric_col]
                            .sum()
                            .reset_index()
                        )

                        activity_daily.rename(
                            columns={
                                metric_col: "activity"
                            },
                            inplace=True
                        )

                        if daily_metrics.empty:

                            daily_metrics = activity_daily

                        else:

                            daily_metrics = daily_metrics.merge(
                                activity_daily,
                                on="date",
                                how="outer"
                            )

            except Exception:
                pass

        # =================================================
        # FINAL PROCESSING
        # =================================================

        if not daily_metrics.empty:

            daily_metrics = daily_metrics.sort_values(
                "date"
            )

            latest_date = pd.to_datetime(
                daily_metrics["date"]
            ).max()

            cutoff = latest_date - pd.Timedelta(
                days=selected_days
            )

            daily_metrics = daily_metrics[
                pd.to_datetime(daily_metrics["date"])
                >= cutoff
            ]

            # Recovery Score

            if "hrv" in daily_metrics.columns:

                recovery = (
                    daily_metrics["hrv"] / 120
                ) * 100

                daily_metrics["recovery"] = np.clip(
                    recovery,
                    0,
                    100
                )

            else:

                daily_metrics["recovery"] = 50

            latest = daily_metrics.iloc[-1]

            # =================================================
            # HERO METRICS
            # =================================================

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Recovery</div>
                    <div class="metric-value">
                        {latest['recovery']:.0f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:

                hrv_value = latest.get("hrv", np.nan)

                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">HRV</div>
                    <div class="metric-value">
                        {hrv_value:.0f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col3:

                hr_value = latest.get(
                    "heart_rate",
                    np.nan
                )

                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Heart Rate</div>
                    <div class="metric-value">
                        {hr_value:.0f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col4:

                act_value = latest.get(
                    "activity",
                    np.nan
                )

                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Activity</div>
                    <div class="metric-value">
                        {act_value:.0f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # =================================================
            # TABS
            # =================================================

            tab1, tab2, tab3 = st.tabs([
                "Overview",
                "Trends",
                "Insights"
            ])

            with tab1:

                st.subheader("Recovery Trend")

                fig = px.line(
                    daily_metrics,
                    x="date",
                    y="recovery"
                )

                fig.update_layout(
                    template="plotly_dark",
                    height=450
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            with tab2:

                numeric = daily_metrics.select_dtypes(
                    include=np.number
                )

                if len(numeric.columns) > 1:

                    corr = numeric.corr()

                    fig = px.imshow(
                        corr,
                        text_auto=True,
                        aspect="auto",
                        title="Correlations"
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

            with tab3:

                st.subheader("AI Insights")

                recovery_avg = (
                    daily_metrics["recovery"]
                    .tail(7)
                    .mean()
                )

                if recovery_avg > 80:

                    st.success(
                        "Recovery trend is strong."
                    )

                elif recovery_avg < 60:

                    st.warning(
                        "Recovery trend is lower than ideal."
                    )

                else:

                    st.info(
                        "Recovery trend is stable."
                    )

            if show_raw:

                st.subheader("Daily Metrics")

                st.dataframe(daily_metrics)

else:

    st.info(
        "Upload your wearable ZIP export."
    )
