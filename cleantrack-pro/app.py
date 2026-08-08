#🧹 CleanTrack Pro
# Smart Cleaning Time Tracker
# Developed by Heider Jeffer


import streamlit as st
from datetime import datetime, time, timedelta

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CleanTrack Pro",
    page_icon="🧹",
    layout="wide"
)

# =========================================================
# CUSTOM UI
# =========================================================

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    color: #777;
    font-size: 18px;
    margin-bottom: 5px;
}

.developer {
    color: #888;
    font-size: 14px;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SETTINGS
# =========================================================

TOTAL_ROOMS = 16

END_TIME = datetime.combine(
    datetime.today(),
    time(13, 0)
)

BREAK_START = datetime.combine(
    datetime.today(),
    time(10, 0)
)

BREAK_END = datetime.combine(
    datetime.today(),
    time(10, 20)
)

# =========================================================
# SESSION STATE
# =========================================================

if "finished_rooms" not in st.session_state:
    st.session_state.finished_rooms = {}

if "rooms_completed" not in st.session_state:
    st.session_state.rooms_completed = 0

# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🧹 CleanTrack Pro</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Smart Cleaning Time Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="developer">'
    'Developed by <b>Heider Jeffer</b>'
    '</div>',
    unsafe_allow_html=True
)

# =========================================================
# CURRENT WORK STATUS
# =========================================================

st.subheader("⚙️ Current Work Status")

col1, col2, col3 = st.columns(3)

with col1:
    current_time_input = st.time_input(
        "Current time",
        value=time(10, 0)
    )

with col2:
    rooms_completed = st.number_input(
        "Rooms already finished",
        min_value=0,
        max_value=TOTAL_ROOMS,
        value=0,
        step=1
    )

with col3:
    corridor_finished = st.checkbox(
        "Corridor already finished",
        value=False
    )

# =========================================================
# CURRENT TIME
# =========================================================

current_time = datetime.combine(
    datetime.today(),
    current_time_input
)

# =========================================================
# ROOMS REMAINING
# =========================================================

rooms_remaining = TOTAL_ROOMS - rooms_completed

# =========================================================
# CALCULATE AVAILABLE TIME
# =========================================================

minutes_available = (
    END_TIME - current_time
).total_seconds() / 60

# Remove the 20-minute break if current time is before break
if current_time < BREAK_START:
    minutes_available -= 20

minutes_available = max(0, minutes_available)

# =========================================================
# MINUTES PER ROOM
# =========================================================

if rooms_remaining > 0:
    minutes_per_room = (
        minutes_available / rooms_remaining
    )
else:
    minutes_per_room = 0

# =========================================================
# FORMAT TIME
# =========================================================

def format_duration(total_minutes):
    total_minutes = max(0, int(round(total_minutes)))

    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours > 0:
        if minutes > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{hours}h"
    else:
        return f"{minutes}m"

# =========================================================
# DASHBOARD
# =========================================================

st.divider()

st.subheader("📊 Current Situation")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Rooms Completed",
        f"{rooms_completed}/{TOTAL_ROOMS}"
    )

with col2:
    st.metric(
        "Rooms Remaining",
        rooms_remaining
    )

with col3:
    st.metric(
        "Time Available",
        format_duration(minutes_available)
    )

with col4:
    st.metric(
        "Minutes / Room",
        f"{minutes_per_room:.1f}"
    )

# =========================================================
# PROGRESS BAR
# =========================================================

progress = rooms_completed / TOTAL_ROOMS

st.progress(progress)

st.write(
    f"**{rooms_completed} of {TOTAL_ROOMS} rooms completed**"
)

# =========================================================
# STATUS
# =========================================================

if rooms_remaining == 0:

    st.success(
        "🎉 All 16 rooms are finished!"
    )

elif minutes_per_room >= 15:

    st.success(
        f"🟢 You have **{minutes_per_room:.1f} minutes "
        "per room**."
    )

elif minutes_per_room >= 10:

    st.warning(
        f"🟡 You have **{minutes_per_room:.1f} minutes "
        "per room**."
    )

else:

    st.error(
        f"🔴 You have only **{minutes_per_room:.1f} minutes "
        "per room**. You are behind schedule."
    )

# =========================================================
# BREAK
# =========================================================

st.divider()

st.subheader("☕ Break")

st.write("**10:00 AM – 10:20 AM**")

# =========================================================
# EXAMPLE
# =========================================================

st.divider()

st.subheader("💡 Example")

st.write(
    "If it is **11:00 AM** and you have finished "
    "**11 rooms**, you have **5 rooms remaining**."
)

st.write(
    "You have **2h 0m** available until 1:00 PM."
)

st.write(
    "That gives you approximately **24 minutes per room**."
)

# =========================================================
# REMAINING SCHEDULE
# =========================================================

st.divider()

st.subheader("🗓️ Remaining Room Plan")

if rooms_remaining > 0:

    schedule_time = current_time

    for room in range(
        rooms_completed + 1,
        TOTAL_ROOMS + 1
    ):

        start = schedule_time

        end = (
            start +
            timedelta(
                minutes=minutes_per_room
            )
        )

        st.write(
            f"🛏️ **Room {room}:** "
            f"{start.strftime('%I:%M %p')} → "
            f"{end.strftime('%I:%M %p')} "
            f"(**{minutes_per_room:.1f} min**)"
        )

        schedule_time = end

else:

    st.success(
        "🏆 All rooms completed!"
    )

# =========================================================
# EXPECTED FINISH
# =========================================================

st.divider()

if rooms_remaining > 0:

    expected_finish = (
        current_time +
        timedelta(
            minutes=(
                rooms_remaining *
                minutes_per_room
            )
        )
    )

    st.info(
        f"🎯 **Expected finish: "
        f"{expected_finish.strftime('%I:%M %p')}**"
    )

else:

    st.success(
        "🎉 Work completed!"
    )

# =========================================================
# INDIVIDUAL ROOM RECORDING
# =========================================================

st.divider()

st.subheader("🛏️ Record Individual Rooms")

st.caption(
    "You can also use these buttons to record rooms "
    "one by one."
)

columns = st.columns(4)

for room in range(1, TOTAL_ROOMS + 1):

    col = columns[(room - 1) % 4]

    with col:

        if room <= rooms_completed:

            st.success(
                f"✅ Room {room} — Completed"
            )

        else:

            if st.button(
                f"Finish Room {room}",
                key=f"finish_{room}",
                use_container_width=True
            ):

                st.session_state.rooms_completed = room

                st.rerun()

# =========================================================
# RESET
# =========================================================

st.divider()

if st.button(
    "🔄 Reset",
    use_container_width=True
):

    st.session_state.rooms_completed = 0
    st.session_state.finished_rooms = {}

    st.rerun()

