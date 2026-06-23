import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="Period Cycle Tracker", layout="centered")

st.title("🩸 Period Cycle Tracker")
st.write("Track your menstrual cycle by recording the first day of your period.")

st.subheader("📍 Record First Day of Cycle")
first_day = st.date_input(
    "Select the first day of your period:",
    value=datetime.now().date(),
    help="Choose the date when your period started"
)

# -- Visualization: hormone trends + phase bands for a 28-day cycle
days = np.arange(1, 29)

# synthetic hormone curves (arbitrary units for visualization)
estrogen = 1.0 + 2.5 * np.exp(-0.5 * ((days - 13) / 3.0) ** 2) + 0.5 * np.exp(-0.5 * ((days - 20) / 4.0) ** 2)
progesterone = 0.5 + 3.0 * np.exp(-0.5 * ((days - 20) / 3.0) ** 2)
lh = 0.2 + 6.0 * np.exp(-0.5 * ((days - 14) / 0.6) ** 2)

# assemble dataframe for Altair
df = pd.DataFrame({
    "day": days,
    "Estrogen": estrogen,
    "Progesterone": progesterone,
    "LH": lh,
})

df_melt = df.melt(id_vars=["day"], var_name="hormone", value_name="value")

# phases for background bands
phases_df = pd.DataFrame([
    {"phase": "Menstruation", "start": 1, "end": 5, "color": "#f28b82"},
    {"phase": "Follicular", "start": 6, "end": 13, "color": "#fbbc04"},
    {"phase": "Ovulation", "start": 14, "end": 14, "color": "#34a853"},
    {"phase": "Luteal", "start": 15, "end": 28, "color": "#aecbfa"},
])

# phase bands
bands = alt.Chart(phases_df).mark_rect(opacity=0.12).encode(
    x=alt.X("start:Q", title="Day of Cycle", scale=alt.Scale(domain=[1, 28])),
    x2="end:Q",
    color=alt.Color("phase:N", legend=None),
    tooltip=[alt.Tooltip("phase:N", title="Phase"), alt.Tooltip("start:Q", title="Start"), alt.Tooltip("end:Q", title="End")],
)

# hormone lines
lines = alt.Chart(df_melt).mark_line(point=True).encode(
    x=alt.X("day:Q", title="Day of Cycle", scale=alt.Scale(domain=[1, 28])),
    y=alt.Y("value:Q", title="Relative Level"),
    color=alt.Color("hormone:N", title="Hormone"),
    tooltip=[alt.Tooltip("day:Q", title="Day"), alt.Tooltip("hormone:N", title="Hormone"), alt.Tooltip("value:Q", title="Level")],
)

chart = (bands + lines).properties(width=700, height=300)

st.subheader("📈 Hormone Trends & Phases")
st.caption("Synthetic trends for Estrogen, Progesterone and LH across a 28-day cycle.")
st.altair_chart(chart, use_container_width=True)

today = datetime.now().date()
cycle_day = (today - first_day).days + 1

st.subheader("📊 Cycle Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Cycle Day", f"Day {cycle_day if cycle_day > 0 else 'N/A'}")

with col2:
    days_ago = (today - first_day).days
    st.metric("Days Since Start", f"{days_ago} days" if days_ago >= 0 else "Future date")

with col3:
    avg_cycle_length = 28
    next_period = first_day + timedelta(days=avg_cycle_length)
    days_until = (next_period - today).days
    st.metric("Days Until Next", f"{days_until} days" if days_until >= 0 else "Overdue")

st.subheader("📅 Cycle Phases (28-day cycle)")

phases = {
    "Menstruation": (1, 5),
    "Follicular": (6, 13),
    "Ovulation": (14, 14),
    "Luteal": (15, 28)
}

for phase_name, (start, end) in phases.items():
    if start <= cycle_day <= end:
        st.success(f"**{phase_name}** (Days {start}-{end}) ← You are here")
    else:
        st.info(f"{phase_name} (Days {start}-{end})")

st.subheader("ℹ️ Details")
st.write(f"**First day recorded:** {first_day.strftime('%A, %B %d, %Y')}")
st.write(f"**Today's date:** {today.strftime('%A, %B %d, %Y')}")

if cycle_day > 0:
    st.write(f"**Current cycle day:** Day {cycle_day}")
else:
    st.warning("Please select a date that is today or in the past.")
