import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import altair as alt
import calendar
import json
import os

st.set_page_config(page_title="Period Cycle Tracker", layout="centered")

# Data persistence
DATA_FILE = "users_data.json"

def load_users_data():
    """Load user data from JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                # Convert string dates back to date objects
                for username in data:
                    for record in data[username].get("records", []):
                        record["period_start"] = datetime.strptime(record["period_start"], "%Y-%m-%d").date()
                        record["period_end"] = datetime.strptime(record["period_end"], "%Y-%m-%d").date()
                        record["skin_date"] = datetime.strptime(record["skin_date"], "%Y-%m-%d").date()
                return data
        except Exception as e:
            st.warning(f"Error loading data: {e}")
            return {}
    return {}

def save_users_data(users_data):
    """Save user data to JSON file."""
    try:
        # Convert date objects to strings for JSON serialization
        data_to_save = {}
        for username, user_info in users_data.items():
            data_to_save[username] = {"password": user_info["password"], "records": []}
            for record in user_info.get("records", []):
                data_to_save[username]["records"].append({
                    "period_start": record["period_start"].isoformat(),
                    "period_end": record["period_end"].isoformat(),
                    "skin_date": record["skin_date"].isoformat(),
                    "skin_status": record["skin_status"],
                    "skin_notes": record["skin_notes"],
                })
        with open(DATA_FILE, "w") as f:
            json.dump(data_to_save, f, indent=2)
    except Exception as e:
        st.error(f"Error saving data: {e}")

st.title("🩸 Period Cycle Tracker")
st.write("Track your menstrual cycle, record your period start, and log your skin status.")

if "users" not in st.session_state:
    st.session_state.users = load_users_data()
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "auth_username" not in st.session_state:
    st.session_state.auth_username = ""
if "auth_password" not in st.session_state:
    st.session_state.auth_password = ""
if "selected_record_index" not in st.session_state:
    st.session_state.selected_record_index = -1
if "selected_record_index_target" not in st.session_state:
    st.session_state.selected_record_index_target = None
if "form_loaded_for" not in st.session_state:
    st.session_state.form_loaded_for = -1
if "period_start_date" not in st.session_state:
    st.session_state.period_start_date = datetime.now().date()
if "period_end_date" not in st.session_state:
    st.session_state.period_end_date = st.session_state.period_start_date + timedelta(days=4)
if "skin_record_date" not in st.session_state:
    st.session_state.skin_record_date = datetime.now().date()
if "skin_status" not in st.session_state:
    st.session_state.skin_status = []
if "skin_notes" not in st.session_state:
    st.session_state.skin_notes = ""
if "calendar_view_month" not in st.session_state:
    st.session_state.calendar_view_month = datetime.now().date().month
if "calendar_view_year" not in st.session_state:
    st.session_state.calendar_view_year = datetime.now().date().year

if st.session_state.current_user is None:
    st.subheader("🔐 Sign in or create an account")
    st.session_state.auth_username = st.text_input("Username", value=st.session_state.auth_username)
    st.session_state.auth_password = st.text_input("Password", value=st.session_state.auth_password, type="password")
    if st.button("Log in"):
        username = st.session_state.auth_username.strip()
        password = st.session_state.auth_password
        if not username or not password:
            st.error("Please enter both a username and a password.")
        elif username in st.session_state.users:
            if st.session_state.users[username]["password"] != password:
                st.error("Username already exists. Please enter the correct password or choose a different username.")
            else:
                st.success(f"Logged in as {username}.")
                st.session_state.current_user = username
                st.session_state.selected_record_index = -1
                st.session_state.form_loaded_for = -1
                st.session_state.period_start_date = datetime.now().date()
                st.session_state.period_end_date = st.session_state.period_start_date + timedelta(days=4)
                st.session_state.skin_record_date = datetime.now().date()
                st.session_state.skin_status = []
                st.session_state.skin_notes = ""
                save_users_data(st.session_state.users)
                st.rerun()
        else:
            st.session_state.users[username] = {"password": password, "records": []}
            st.success(f"Account created and logged in as {username}.")
            st.session_state.current_user = username
            st.session_state.selected_record_index = -1
            st.session_state.form_loaded_for = -1
            st.session_state.period_start_date = datetime.now().date()
            st.session_state.period_end_date = st.session_state.period_start_date + timedelta(days=4)
            st.session_state.skin_record_date = datetime.now().date()
            st.session_state.skin_status = []
            st.session_state.skin_notes = ""
            save_users_data(st.session_state.users)
            st.rerun()
    st.stop()

with st.sidebar:
    st.markdown(f"**Logged in as:** {st.session_state.current_user}")
    if st.button("Log out"):
        st.session_state.current_user = None
        st.session_state.selected_record_index = -1
        st.session_state.form_loaded_for = -1
        st.session_state.period_start_date = datetime.now().date()
        st.session_state.period_end_date = st.session_state.period_start_date + timedelta(days=4)
        st.session_state.skin_record_date = datetime.now().date()
        st.session_state.skin_status = []
        st.session_state.skin_notes = ""
        st.rerun()

tabs = st.tabs(["Cycle Tracker", "Record Cycle & Skin Status"])

with tabs[1]:
    st.subheader("📝 Record Cycle & Skin Status")

    symbol_map = {
        "Clear": "🌸",
        "Dry": "💧",
        "Oily": "🟡",
        "Breakouts": "⚠️",
        "Sensitive": "🌿",
        "Dull": "⚫",
    }

    def render_calendar(year, month, records):
        month_calendar = calendar.monthcalendar(year, month)
        period_days = set()
        status_by_day = {}
        for record in records:
            start = record["period_start"]
            end = record["period_end"]
            if start and end:
                for offset in range((end - start).days + 1):
                    record_day = start + timedelta(days=offset)
                    if record_day.year == year and record_day.month == month:
                        period_days.add(record_day.day)
            skin_date = record["skin_date"]
            if skin_date.year == year and skin_date.month == month and record["skin_status"]:
                status_by_day.setdefault(skin_date.day, set()).update(record["skin_status"])

        html = "<style>.cal-table {width:100%; table-layout: fixed; border-collapse: collapse;}.cal-table th, .cal-table td {border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: top; min-height: 140px;}.cal-day {font-weight: 700; margin-bottom: 4px;}.period-day {background-color: rgba(211, 47, 47, 0.16);}.status-icons {font-size: 18px; display:flex; flex-wrap: wrap; justify-content:center; gap:4px; margin-top:6px;}</style>"
        html += "<table class='cal-table'><tr>"
        for day_name in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            html += f"<th>{day_name}</th>"
        html += "</tr>"
        for week in month_calendar:
            html += "<tr>"
            for day in week:
                if day == 0:
                    html += "<td></td>"
                else:
                    td_class = "period-day" if day in period_days else ""
                    cell_html = f"<div class='cal-day'>{day}</div>"
                    if day in status_by_day:
                        cell_html += "<div class='status-icons'>"
                        for status in sorted(status_by_day[day]):
                            icon = symbol_map.get(status, "")
                            cell_html += f"{icon}"
                        cell_html += "</div>"
                    html += f"<td class='{td_class}'>{cell_html}</td>"
            html += "</tr>"
        html += "</table>"
        return html

    user_records = st.session_state.users[st.session_state.current_user]["records"]
    record_count = len(user_records)
    record_options = [-1] + list(range(record_count))
    record_labels = { -1: "Create new record" }
    for idx, rec in enumerate(user_records):
        record_labels[idx] = f"{idx + 1}: {rec['skin_date'].strftime('%b %d, %Y')} (start {rec['period_start'].strftime('%b %d')})"

    if st.session_state.selected_record_index_target is not None:
        if st.session_state.selected_record_index_target in record_options:
            st.session_state.selected_record_index = st.session_state.selected_record_index_target
        st.session_state.selected_record_index_target = None

    if st.session_state.selected_record_index not in record_options:
        st.session_state.selected_record_index = -1

    selected_record_index = st.selectbox(
        "Select record to edit",
        record_options,
        format_func=lambda idx: record_labels[idx],
        index=record_options.index(st.session_state.selected_record_index),
        key="selected_record_index"
    )

    if selected_record_index != -1 and st.session_state.form_loaded_for != selected_record_index:
        selected_record = user_records[selected_record_index]
        st.session_state.period_start_date = selected_record["period_start"]
        st.session_state.period_end_date = selected_record["period_end"]
        st.session_state.skin_record_date = selected_record["skin_date"]
        st.session_state.skin_status = selected_record["skin_status"]
        st.session_state.skin_notes = selected_record["skin_notes"]
        st.session_state.form_loaded_for = selected_record_index
    elif selected_record_index == -1 and st.session_state.form_loaded_for != -1:
        st.session_state.period_start_date = datetime.now().date()
        st.session_state.period_end_date = st.session_state.period_start_date + timedelta(days=4)
        st.session_state.skin_record_date = datetime.now().date()
        st.session_state.skin_status = []
        st.session_state.skin_notes = ""
        st.session_state.form_loaded_for = -1

    period_start = st.session_state.period_start_date
    period_end = st.session_state.period_end_date
    skin_record_date = st.session_state.skin_record_date
    skin_status = st.session_state.skin_status

    month_names = list(calendar.month_name)[1:]
    col_month, col_year = st.columns(2)
    with col_month:
        display_month = st.selectbox(
            "View month",
            list(range(1, 13)),
            format_func=lambda x: month_names[x - 1],
            index=st.session_state.calendar_view_month - 1,
            key="calendar_view_month"
        )
    with col_year:
        display_year = st.number_input(
            "View year",
            min_value=2020,
            max_value=2050,
            value=st.session_state.calendar_view_year,
            key="calendar_view_year"
        )

    st.markdown("### Calendar")
    st.markdown(render_calendar(display_year, display_month, user_records), unsafe_allow_html=True)
    st.markdown("**Legend:** red shading = Period  •  🌸 Clear  •  💧 Dry  •  🟡 Oily  •  ⚠️ Breakouts  •  🌿 Sensitive  •  ⚫ Dull")

    symptom_options = ["Clear", "Dry", "Oily", "Breakouts", "Sensitive", "Dull"]
    selected_symptom = st.selectbox("Show frequency for", symptom_options, index=symptom_options.index("Breakouts"))

    symptom_summary = []
    for record in user_records:
        if selected_symptom in record["skin_status"]:
            cycle_day = (record["skin_date"] - record["period_start"]).days + 1
            if 1 <= cycle_day <= 28:
                symptom_summary.append({"day": cycle_day, "count": 1})

    if symptom_summary:
        symptom_df = pd.DataFrame(symptom_summary).groupby("day", as_index=False).sum()
        symptom_df["average_per_record"] = symptom_df["count"] / max(len(user_records), 1)
        symptom_chart = alt.Chart(symptom_df).mark_bar(color="#d32f2f").encode(
            x=alt.X("day:O", title="Cycle Day"),
            y=alt.Y("count:Q", title=f"{selected_symptom} Count"),
            tooltip=[
                alt.Tooltip("day:O", title="Day"),
                alt.Tooltip("count:Q", title=f"{selected_symptom} occurrences"),
                alt.Tooltip("average_per_record:Q", title="Average per saved record", format=".2f"),
            ]
        ).properties(width=700, height=300)
        st.subheader(f"📊 {selected_symptom} Frequency by Cycle Day")
        st.caption(f"Based on saved records. Each bar shows how often {selected_symptom} was recorded on that cycle day.")
        st.altair_chart(symptom_chart, use_container_width=True)
    else:
        st.info(f"Save a record with {selected_symptom} to see its frequency by cycle day.")

    period_start = st.date_input(
        "Period start date:",
        value=st.session_state.period_start_date,
        help="Record the first day of your period.",
        key="period_start_date"
    )
    period_end = st.date_input(
        "Period end date (optional):",
        value=st.session_state.period_end_date,
        help="Record the last day of your menstrual bleeding.",
        key="period_end_date"
    )
    skin_record_date = st.date_input(
        "Skin record date:",
        value=st.session_state.skin_record_date,
        help="Record the date when you logged your skin status.",
        key="skin_record_date"
    )

    status_options = ["Clear", "Dry", "Oily", "Breakouts", "Sensitive", "Dull"]
    skin_status = st.multiselect(
        "Select all skin conditions that apply:",
        status_options,
        default=st.session_state.skin_status,
        key="skin_status"
    )
    skin_notes = st.text_area(
        "Skin notes (optional)",
        value=st.session_state.skin_notes,
        help="Record texture, hydration, blemishes, redness, or sensitivities.",
        key="skin_notes"
    )

    if st.button("Save cycle and skin status"):
        saved_record = {
            "period_start": period_start,
            "period_end": period_end,
            "skin_date": skin_record_date,
            "skin_status": skin_status,
            "skin_notes": skin_notes,
        }
        if selected_record_index != -1 and selected_record_index < len(user_records):
            user_records[selected_record_index] = saved_record
            st.success("Updated selected record.")
        else:
            user_records.append(saved_record)
            st.success("Saved period and skin status records.")
            st.session_state.selected_record_index_target = len(user_records) - 1
            st.session_state.form_loaded_for = st.session_state.selected_record_index_target
        save_users_data(st.session_state.users)

    st.markdown("---")
    st.subheader("Latest saved entry")
    latest_record = None
    if user_records:
        if selected_record_index != -1 and selected_record_index < len(user_records):
            latest_record = user_records[selected_record_index]
        else:
            latest_record = user_records[-1]

    if latest_record is not None:
        st.write(f"**Recorded period start:** {latest_record['period_start'].strftime('%A, %B %d, %Y')}")
        st.write(f"**Recorded period end:** {latest_record['period_end'].strftime('%A, %B %d, %Y')}")
        st.write(f"**Skin record date:** {latest_record['skin_date'].strftime('%A, %B %d, %Y')}")
        st.write(f"**Skin status:** {', '.join(latest_record['skin_status']) if latest_record['skin_status'] else 'Not recorded yet.'}")
        if latest_record['skin_notes']:
            st.write(f"**Notes:** {latest_record['skin_notes']}")
    else:
        st.info("No saved records yet. Use the form above to save your first record.")

with tabs[0]:
    st.subheader("📍 Current Cycle Tracker")
    user_records = st.session_state.users.get(st.session_state.current_user, {}).get("records", [])
    latest_record = None
    if user_records:
        latest_record = user_records[-1]
    first_day = latest_record["period_start"] if latest_record is not None else st.session_state.period_start_date
    today = datetime.now().date()
    cycle_day = (today - first_day).days + 1

    if cycle_day < 1:
        st.warning("The saved cycle start date is in the future. Please update it in the Record Cycle & Skin Status tab.")

    days = np.arange(1, 29)
    estrogen = 1.0 + 2.5 * np.exp(-0.5 * ((days - 13) / 3.0) ** 2) + 0.5 * np.exp(-0.5 * ((days - 20) / 4.0) ** 2)
    progesterone = 0.5 + 3.0 * np.exp(-0.5 * ((days - 20) / 3.0) ** 2)
    lh = 0.2 + 6.0 * np.exp(-0.5 * ((days - 14) / 0.6) ** 2)

    df = pd.DataFrame({
        "day": days,
        "Estrogen": estrogen,
        "Progesterone": progesterone,
        "LH": lh,
    })
    df_melt = df.melt(id_vars=["day"], var_name="hormone", value_name="value")

    phases_df = pd.DataFrame([
        {"phase": "Menstruation", "start": 1, "end": 5, "color": "#f28b82"},
        {"phase": "Follicular", "start": 6, "end": 13, "color": "#fbbc04"},
        {"phase": "Ovulation", "start": 14, "end": 14, "color": "#34a853"},
        {"phase": "Luteal", "start": 15, "end": 28, "color": "#aecbfa"},
    ])
    bands = alt.Chart(phases_df).mark_rect(opacity=0.12).encode(
        x=alt.X("start:Q", title="Day of Cycle", scale=alt.Scale(domain=[1, 28])),
        x2="end:Q",
        color=alt.Color("phase:N", legend=None),
        tooltip=[alt.Tooltip("phase:N", title="Phase"), alt.Tooltip("start:Q", title="Start"), alt.Tooltip("end:Q", title="End")],
    )
    lines = alt.Chart(df_melt).mark_line(point=True).encode(
        x=alt.X("day:Q", title="Day of Cycle", scale=alt.Scale(domain=[1, 28])),
        y=alt.Y("value:Q", title="Relative Level"),
        color=alt.Color("hormone:N", title="Hormone", legend=alt.Legend(title="Hormone Lines", orient="top-right")),
        tooltip=[alt.Tooltip("day:Q", title="Day"), alt.Tooltip("hormone:N", title="Hormone"), alt.Tooltip("value:Q", title="Level")],
    )
    marker = None
    if 1 <= cycle_day <= 28:
        marker_df = pd.DataFrame({"day": [int(cycle_day)], "label": [f"Today: Day {int(cycle_day)}"]})
        marker = alt.Chart(marker_df).mark_rule(color="red", strokeWidth=2).encode(
            x=alt.X("day:Q"),
            tooltip=[alt.Tooltip("label:N", title="Info"), alt.Tooltip("day:Q", title="Day")],
        )
    if marker is not None:
        chart = (bands + lines + marker).properties(width=700, height=300)
    else:
        chart = (bands + lines).properties(width=700, height=300)

    st.subheader("📈 Hormone Trends & Phases")
    st.caption("Synthetic trends for Estrogen, Progesterone and LH across a 28-day cycle.")
    st.write("🔵 Estrogen  🟠 Progesterone  🔴 LH  ")
    st.altair_chart(chart, use_container_width=True)

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

    current_phase = None
    for name, (s, e) in phases.items():
        if s <= cycle_day <= e:
            current_phase = name
            break

    phase_advice = {
        "Menstruation": {
            "skin": "May be sensitive, drier, or have breakouts; favor hydrating, barrier-repairing products.",
            "body": "Expect cramps, low energy and bloating; use heat and gentle movement.",
            "emotion": "Lower mood and fatigue; prioritize rest and soothing routines.",
            "recommendation": "Use fragrance-free hydrators, avoid strong exfoliants, gentle yoga and warm compresses."
        },
        "Follicular": {
            "skin": "Skin often looks brighter and more resilient as estrogen rises.",
            "body": "Energy increases; good window for strength and HIIT workouts.",
            "emotion": "Improved motivation and focus.",
            "recommendation": "Introduce active skincare (vitamin C, gentle exfoliation) and schedule demanding tasks or treatments."
        },
        "Ovulation": {
            "skin": "Peak radiance; some may notice increased oiliness.",
            "body": "Peak strength and libido; good endurance.",
            "emotion": "Confident and social.",
            "recommendation": "Great time for photos or important meetings; keep sunscreen and oil-control products handy."
        },
        "Luteal": {
            "skin": "Progesterone can increase oil and premenstrual breakouts.",
            "body": "Bloating, breast tenderness, possible sleep changes.",
            "emotion": "Mood swings, increased anxiety or PMS symptoms.",
            "recommendation": "Use spot treatments for breakouts, calm barrier-supporting skincare, reduce caffeine/sugar, and try magnesium or relaxation practices."
        }
    }

    st.subheader("🔎 Phase-specific Skin · Body · Emotion")
    if current_phase and current_phase in phase_advice:
        advice = phase_advice[current_phase]
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("**Skin**")
            st.write(advice["skin"])
        with col_b:
            st.markdown("**Body**")
            st.write(advice["body"])
        with col_c:
            st.markdown("**Emotion**")
            st.write(advice["emotion"])
        st.write("**Recommendation:** " + advice["recommendation"])
    else:
        st.info("Select a valid first day to see phase-specific advice.")

    st.subheader("🔖 Saved Skin Status")
    st.write(f"**Skin status:** {st.session_state.skin_status or 'Not recorded yet.'}")
    if st.session_state.skin_notes:
        st.write(f"**Skin notes:** {st.session_state.skin_notes}")

    st.subheader("ℹ️ Details")
    st.write(f"**First day recorded:** {first_day.strftime('%A, %B %d, %Y')}")
    st.write(f"**Today's date:** {today.strftime('%A, %B %d, %Y')}")
    if cycle_day > 0:
        st.write(f"**Current cycle day:** Day {cycle_day}")
    else:
        st.warning("Please select a date that is today or in the past.")
