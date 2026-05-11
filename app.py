import streamlit as st import pandas as pd import numpy as np import plotly.express as px import plotly.graph_objects as go from pathlib import Path

st.set_page_config( page_title="Wearable Analytics Dashboard", layout="wide" )

st.title("Personal Wearable Analytics Dashboard") st.caption("Zepp + Health Connect Analytics")

=====================================================

DATA PATHS

=====================================================

DATA_PATH = Path("data/zepp")

=====================================================

HELPERS

=====================================================

@st.cache_data

def safe_load_csv(filename):

file_path = DATA_PATH / filename

if not file_path.exists():
    return pd.DataFrame()

try:
    df = pd.read_csv(file_path)
    return df

except Exception as e:
    st.warning(f"Could not load {filename}: {e}")
    return pd.DataFrame()

def find_column(df, possible_names):

cols = [c.lower() for c in df.columns]

for name in possible_names:
    if name.lower() in cols:
        return df.columns[cols.index(name.lower())]

return None

=====================================================

LOAD FILES

=====================================================

sleep_df = safe_load_csv("sleep.csv") activity_df = safe_load_csv("activity.csv") heart_df = safe_load_csv("heart_rate.csv") workout_df = safe_load_csv("workouts.csv")

=====================================================

SIDEBAR

=====================================================

st.sidebar.title("Dashboard Controls")

show_raw = st.sidebar.checkbox("Show Raw Data")

=====================================================

SLEEP PROCESSING

=====================================================

sleep_daily = pd.DataFrame()

if not sleep_df.empty:

start_col = find_column(
    sleep_df,
    ["start_time", "start", "sleep_start", "bed_time"]
)

end_col = find_column(
    sleep_df,
    ["end_time", "end", "sleep_end", "wake_time"]
)

if start_col and end_col:

    sleep_df[start_col] = pd.to_datetime(
        sleep_df[start_col],
        errors="coerce"
    )

    sleep_df[end_col] = pd.to_datetime(
        sleep_df[end_col],
        errors="coerce"
    )

    sleep_df["sleep_hours"] = (
        sleep_df[end_col] - sleep_df[start_col]
    ).dt.total_seconds() / 3600

    sleep_df["date"] = sleep_df[start_col].dt.date

    sleep_daily = (
        sleep_df.groupby("date")
        ["sleep_hours"]
        .mean()
        .reset_index()
    )

=====================================================

ACTIVITY PROCESSING

=====================================================

activity_daily = pd.DataFrame()

if not activity_df.empty:

date_col = find_column(
    activity_df,
    ["date", "start_time", "time"]
)

steps_col = find_column(
    activity_df,
    ["steps", "step", "step_count"]
)

calories_col = find_column(
    activity_df,
    ["calories", "calorie", "active_calories"]
)

if date_col:

    activity_df[date_col] = pd.to_datetime(
        activity_df[date_col],
        errors="coerce"
    )

    activity_df["date"] = activity_df[date_col].dt.date

    agg_dict = {}

    if steps_col:
        agg_dict[steps_col] = "sum"

    if calories_col:
        agg_dict[calories_col] = "sum"

    if agg_dict:

        activity_daily = (
            activity_df.groupby("date")
            .agg(agg_dict)
            .reset_index()
        )

        rename_map = {}

        if steps_col:
            rename_map[steps_col] = "steps"

        if calories_col:
            rename_map[calories_col] = "calories"

        activity_daily.rename(columns=rename_map, inplace=True)

=====================================================

HEART RATE PROCESSING

=====================================================

heart_daily = pd.DataFrame()

if not heart_df.empty:

hr_col = find_column(
    heart_df,
    ["heart_rate", "hr", "bpm", "beats_per_minute"]
)

hr_time_col = find_column(
    heart_df,
    ["time", "date", "timestamp", "start_time"]
)

if hr_col and hr_time_col:

    heart_df[hr_time_col] = pd.to_datetime(
        heart_df[hr_time_col],
        errors="coerce"
    )

    heart_df["date"] = heart_df[hr_time_col].dt.date

    heart_daily = (
        heart_df.groupby("date")
        [hr_col]
        .mean()
        .reset_index()
    )

    heart_daily.rename(
        columns={hr_col: "avg_hr"},
        inplace=True
    )

=====================================================

MERGE DAILY METRICS

=====================================================

merged = pd.DataFrame()

for df in [sleep_daily, activity_daily, heart_daily]:

if not df.empty:

    if merged.empty:
        merged = df.copy()
    else:
        merged = merged.merge(df, on="date", how="outer")

if not merged.empty:

merged = merged.sort_values("date")

=====================================================

RECOVERY SCORE

=====================================================

if not merged.empty:

merged["sleep_score"] = np.clip(
    (merged.get("sleep_hours", 0) / 8) * 100,
    0,
    100
)

if "avg_hr" in merged.columns:

    hr_min = merged["avg_hr"].min()
    hr_max = merged["avg_hr"].max()

    merged["hr_score"] = 100 - (
        (merged["avg_hr"] - hr_min)
        /
        (hr_max - hr_min + 1e-9)
    ) * 100

else:

    merged["hr_score"] = 50

merged["recovery_score"] = (
    merged["sleep_score"] * 0.6 +
    merged["hr_score"] * 0.4
)

=====================================================

TOP METRICS

=====================================================

if not merged.empty:

latest = merged.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Recovery Score",
        f"{latest['recovery_score']:.0f}"
    )

with col2:
    if "sleep_hours" in latest:
        st.metric(
            "Sleep Hours",
            f"{latest['sleep_hours']:.1f}h"
        )

with col3:
    if "steps" in latest:
        st.metric(
            "Steps",
            f"{int(latest['steps']):,}"
        )

with col4:
    if "avg_hr" in latest:
        st.metric(
            "Avg Heart Rate",
            f"{latest['avg_hr']:.0f} bpm"
        )

=====================================================

TABS

=====================================================

overview_tab, sleep_tab, activity_tab, recovery_tab, correlation_tab = st.tabs([ "Overview", "Sleep", "Activity", "Recovery", "Correlations" ])

=====================================================

OVERVIEW TAB

=====================================================

with overview_tab:

st.subheader("Daily Recovery Trend")

if not merged.empty:

    fig = px.line(
        merged,
        x="date",
        y="recovery_score",
        title="Recovery Score Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)

=====================================================

SLEEP TAB

=====================================================

with sleep_tab:

st.subheader("Sleep Analytics")

if not sleep_daily.empty:

    fig = px.line(
        sleep_daily,
        x="date",
        y="sleep_hours",
        title="Sleep Duration"
    )

    st.plotly_chart(fig, use_container_width=True)

    avg_sleep = sleep_daily["sleep_hours"].mean()

    st.info(f"Average Sleep: {avg_sleep:.2f} hours")

=====================================================

ACTIVITY TAB

=====================================================

with activity_tab:

st.subheader("Activity Analytics")

if not activity_daily.empty and "steps" in activity_daily.columns:

    fig = px.bar(
        activity_daily,
        x="date",
        y="steps",
        title="Daily Steps"
    )

    st.plotly_chart(fig, use_container_width=True)

    avg_steps = activity_daily["steps"].mean()

    st.info(f"Average Daily Steps: {avg_steps:,.0f}")

=====================================================

RECOVERY TAB

=====================================================

with recovery_tab:

st.subheader("Recovery Analytics")

if not merged.empty:

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=merged["date"],
            y=merged["recovery_score"],
            mode="lines",
            name="Recovery"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

=====================================================

CORRELATIONS TAB

=====================================================

with correlation_tab:

st.subheader("Correlation Analysis")

numeric_cols = merged.select_dtypes(include=np.number)

if not numeric_cols.empty:

    corr = numeric_cols.corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        title="Metric Correlations"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write(corr)

=====================================================

RAW DATA

=====================================================

if show_raw:

st.subheader("Merged Daily Dataset")

st.dataframe(merged)

=====================================================

DEBUGGING

=====================================================

with st.expander("Debug Information"):

st.write("Sleep Columns:", sleep_df.columns.tolist())
st.write("Activity Columns:", activity_df.columns.tolist())
st.write("Heart Columns:", heart_df.columns.tolist())
