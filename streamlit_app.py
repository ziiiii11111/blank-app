import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Period Cycle Tracker", layout="centered")

st.title("🩸 Period Cycle Tracker")
st.write("Track your menstrual cycle by recording the first day of your period.")

st.subheader("📍 Record First Day of Cycle")
first_day = st.date_input(
    "Select the first day of your period:",
    value=datetime.now().date(),
    help="Choose the date when your period started"
)

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
