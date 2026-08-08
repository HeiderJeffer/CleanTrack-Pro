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

START_TIME = datetime.combine(
    datetime.today(),
    time(8, 0)
)

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
# TOP CONTROLS
# =========================================================

col1, col2 = st.columns([3, 1])

with col1:
    st.info(
        "Click **Finish Room** when you finish cleaning a room. "
        "The app will automatically calculate the remaining time."
    )

with col2:
    if st.button(
        "🔄 Reset All",
        use_container_width=True
    ):
        st.session_state.finished_rooms = {}
        st.rerun()

# =========================================================
# CURRENT TIME
# =========================================================

st.subheader("⏰ Current Time")

current_time_input = st.time_input(
    "Set current time",
    value=time(10, 0)
)

current_time = datetime.combine(
    datetime.today(),
    current_time_input
)

# =========================================================
# CALCULATIONS
# =========================================================

rooms_completed = len(
    st.session_state.finished_rooms
)

rooms_remaining = TOTAL_ROOMS - rooms_completed

# Time available until 1:00 PM
minutes_available = (
    END_TIME - current_time
).total_seconds() / 60

# Remove the 20-minute break if it has not happened yet
if current_time < BREAK_START:
    minutes_available -= 20

minutes_available = max(
    0,
    minutes_available
)

# Calculate minutes available per room
if rooms_remaining > 0:
    minutes_per_room = (
        minutes_available / rooms_remaining
    )
else:
    minutes_per_room = 0

# =========================================================
# DASHBOARD
# =========================================================

st.subheader("📊 Your Progress")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Rooms Done",
        f"{rooms_completed}/{TOTAL_ROOMS}"
    )

with col2:
    st.metric(
        "Rooms Left",
        rooms_remaining
    )

with col3:
    st.metric(
        "Time Left",
        f"{minutes_available:.0f} min"
    )

with col4:
    st.metric(
        "Min / Room",
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
        "🎉 Excellent! All 16 rooms are finished."
    )

elif minutes_per_room >= 15:

    st.success(
        f"🟢 You have {minutes_per_room:.1f} minutes "
        "available for each remaining room."
    )

elif minutes_per_room >= 10:

    st.warning(
        f"🟡 You have {minutes_per_room:.1f} minutes "
        "available for each remaining room."
    )

else:

    st.error(
        f"🔴 You have only {minutes_per_room:.1f} minutes "
        "per remaining room. You are behind schedule."
    )

# =========================================================
# BREAK
# =========================================================

st.divider()

st.subheader("☕ Break")

st.write("**10:00 AM – 10:20 AM**")

# =========================================================
# ROOMS
# =========================================================

st.divider()

st.subheader("🛏️ Rooms")

columns = st.columns(4)

for room in range(1, TOTAL_ROOMS + 1):

    col = columns[(room - 1) % 4]

    with col:

        # Room already finished
        if room in st.session_state.finished_rooms:

            finished_at = (
                st.session_state.finished_rooms[room]
            )

            st.success(
                f"✅ Room {room}\n\n"
                f"Finished: {finished_at}"
            )

        # Room not finished
        else:

            if st.button(
                f"🧹 Finish Room {room}",
                key=f"finish_{room}",
                use_container_width=True
            ):

                st.session_state.finished_rooms[
                    room
                ] = current_time.strftime("%H:%M")

                st.rerun()

# =========================================================
# REMAINING SCHEDULE
# =========================================================

st.divider()

st.subheader("🗓️ Remaining Schedule")

if rooms_remaining > 0:

    schedule_time = current_time

    for room in range(1, TOTAL_ROOMS + 1):

        if room not in st.session_state.finished_rooms:

            start = schedule_time

            end = start + timedelta(
                minutes=minutes_per_room
            )

            st.write(
                f"**Room {room}:** "
                f"{start.strftime('%I:%M %p')} → "
                f"{end.strftime('%I:%M %p')} "
                f"({minutes_per_room:.1f} min)"
            )

            schedule_time = end

else:

    st.success("No rooms remaining.")

# =========================================================
# FINISH TIME
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
        f"🎯 **Expected finish:** "
        f"{expected_finish.strftime('%I:%M %p')}"
    )

else:

    st.success("🏆 Work completed!")