import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import altair as alt
import calendar

st.set_page_config(page_title="Period Cycle Tracker", layout="centered")

st.title("🩸 Period Cycle Tracker")
st.write("Track your menstrual cycle, record your period start, and log your skin status.")

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

tabs = st.tabs(["Cycle Tracker", "Record Cycle & Skin Status"])

with tabs[1]:
    st.subheader("📝 Record Cycle & Skin Status")
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

    symbol_map = {
        "Clear": "🌸",
        "Dry": "💧",
        "Oily": "🟡",
        "Breakouts": "⚠️",
        "Sensitive": "🌿",
        "Dull": "⚫",
    }

    def render_calendar(year, month, period_start_date, period_end_date, skin_date, statuses):
        month_calendar = calendar.monthcalendar(year, month)
        html = "<style>.cal-table {width:100%; table-layout: fixed; border-collapse: collapse;}.cal-table th, .cal-table td {border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: top; min-height: 140px;}.cal-day {font-weight: 700; margin-bottom: 4px;}.period-dot {color: #d32f2f; font-size: 18px;}.status-icons {font-size: 18px; display:flex; flex-wrap: wrap; justify-content:center; gap:4px; margin-top:6px;}</style>"
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
                    cell_html = f"<div class='cal-day'>{day}</div>"
                    if period_start_date and period_end_date and period_start_date <= datetime(year, month, day).date() <= period_end_date:
                        cell_html += f"<div class='period-dot'>🔴</div>"
                    if skin_date and day == skin_date.day and skin_date.month == month and skin_date.year == year and statuses:
                        cell_html += "<div class='status-icons'>"
                        for status in statuses:
                            icon = symbol_map.get(status, "")
                            cell_html += f"{icon}"
                        cell_html += "</div>"
                    html += f"<td>{cell_html}</td>"
            html += "</tr>"
        html += "</table>"
        return html

    display_month = skin_record_date.month if skin_record_date else period_start.month
    display_year = skin_record_date.year if skin_record_date else period_start.year
    st.markdown("### Calendar")
    st.markdown(render_calendar(display_year, display_month, period_start, period_end, skin_record_date, skin_status), unsafe_allow_html=True)
    st.markdown("**Legend:** 🔴 Period  •  🌸 Clear  •  💧 Dry  •  🟡 Oily  •  ⚠️ Breakouts  •  🌿 Sensitive  •  ⚫ Dull")

    if st.button("Save cycle and skin status"):
        st.session_state.period_start_date = period_start
        st.session_state.period_end_date = period_end
        st.session_state.skin_record_date = skin_record_date
        st.session_state.skin_status = skin_status
        st.session_state.skin_notes = skin_notes
        st.success("Saved period and skin status records.")

    st.markdown("---")
    st.subheader("Latest saved entry")
    st.write(f"**Recorded period start:** {st.session_state.period_start_date.strftime('%A, %B %d, %Y')}")
    st.write(f"**Recorded period end:** {st.session_state.period_end_date.strftime('%A, %B %d, %Y')}")
    st.write(f"**Skin record date:** {st.session_state.skin_record_date.strftime('%A, %B %d, %Y')}")
    st.write(f"**Skin status:** {', '.join(st.session_state.skin_status) if st.session_state.skin_status else 'Not recorded yet.'}")
    if st.session_state.skin_notes:
        st.write(f"**Notes:** {st.session_state.skin_notes}")

with tabs[0]:
    st.subheader("📍 Current Cycle Tracker")
    first_day = st.session_state.period_start_date
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
