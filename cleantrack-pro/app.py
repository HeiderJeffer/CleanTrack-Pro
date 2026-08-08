# CleanTrack Pro
# Smart Cleaning Time Tracker
# Developed by Heider Jeffer

import streamlit as st
from datetime import datetime, time, timedelta
from supabase import create_client
import pandas as pd


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CleanTrack Pro",
    page_icon="🧹",
    layout="wide"
)


# =========================================================
# SUPABASE CONNECTION
# =========================================================

@st.cache_resource
def init_supabase():

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)


supabase = init_supabase()


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

if "room_notes" not in st.session_state:

    st.session_state.room_notes = {
        room: ""
        for room in range(1, TOTAL_ROOMS + 1)
    }


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
# TABS
# =========================================================

dashboard_tab, history_tab = st.tabs(
    ["🧹 Dashboard", "📚 History"]
)


# =========================================================
# DASHBOARD
# =========================================================

with dashboard_tab:

    # -----------------------------------------------------
    # AUTOMATIC DATE
    # -----------------------------------------------------

    today = datetime.now()

    st.subheader("📅 Working Day")

    st.info(
        f"Today: **{today.strftime('%d/%m/%Y')}**"
    )

    # -----------------------------------------------------
    # CURRENT WORK STATUS
    # -----------------------------------------------------

    st.subheader("⚙️ Current Work Status")

    col1, col2, col3 = st.columns(3)

    with col1:

        current_time_input = st.time_input(
            "Current time",
            value=time(8, 0)
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

    # -----------------------------------------------------
    # CURRENT TIME
    # -----------------------------------------------------

    current_time = datetime.combine(
        datetime.today(),
        current_time_input
    )

    # -----------------------------------------------------
    # ROOMS REMAINING
    # -----------------------------------------------------

    rooms_remaining = (
        TOTAL_ROOMS - rooms_completed
    )

    # -----------------------------------------------------
    # AVAILABLE TIME
    # -----------------------------------------------------

    minutes_available = (
        END_TIME - current_time
    ).total_seconds() / 60

    # Remove 20-minute break if it has not happened yet
    if current_time < BREAK_START:

        minutes_available -= 20

    minutes_available = max(
        0,
        minutes_available
    )

    # -----------------------------------------------------
    # MINUTES PER ROOM
    # -----------------------------------------------------

    if rooms_remaining > 0:

        minutes_per_room = (
            minutes_available /
            rooms_remaining
        )

    else:

        minutes_per_room = 0

    # -----------------------------------------------------
    # FORMAT TIME
    # -----------------------------------------------------

    def format_duration(total_minutes):

        total_minutes = max(
            0,
            int(round(total_minutes))
        )

        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours > 0:

            if minutes > 0:
                return f"{hours}h {minutes}m"

            return f"{hours}h"

        return f"{minutes}m"

    # -----------------------------------------------------
    # DASHBOARD METRICS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # PROGRESS
    # -----------------------------------------------------

    progress = (
        rooms_completed /
        TOTAL_ROOMS
    )

    st.progress(progress)

    st.write(
        f"**{rooms_completed} of "
        f"{TOTAL_ROOMS} rooms completed**"
    )

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    if rooms_remaining == 0:

        st.success(
            "🎉 All 16 rooms are finished!"
        )

    elif minutes_per_room >= 15:

        st.success(
            f"🟢 You have "
            f"**{minutes_per_room:.1f} minutes "
            f"per room**."
        )

    elif minutes_per_room >= 10:

        st.warning(
            f"🟡 You have "
            f"**{minutes_per_room:.1f} minutes "
            f"per room**."
        )

    else:

        st.error(
            f"🔴 You have only "
            f"**{minutes_per_room:.1f} minutes "
            f"per room**."
        )

    # -----------------------------------------------------
    # BREAK
    # -----------------------------------------------------

    st.divider()

    st.subheader("☕ Break")

    st.write("**10:00 AM – 10:20 AM**")

    # -----------------------------------------------------
    # REMAINING SCHEDULE
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # EXPECTED FINISH
    # -----------------------------------------------------

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

        expected_finish_text = (
            expected_finish.strftime(
                "%I:%M %p"
            )
        )

        st.info(
            f"🎯 **Expected finish: "
            f"{expected_finish_text}**"
        )

    else:

        expected_finish_text = (
            current_time.strftime(
                "%I:%M %p"
            )
        )

        st.success(
            "🎉 Work completed!"
        )

    # -----------------------------------------------------
    # ROOM NOTES
    # -----------------------------------------------------

    st.divider()

    st.subheader("📝 Worker Notes")

    st.caption(
        "Add any information about a room."
    )

    for room in range(
        1,
        TOTAL_ROOMS + 1
    ):

        st.session_state.room_notes[room] = st.text_area(
            f"Room {room} – Notes",
            value=st.session_state.room_notes[room],
            placeholder=(
                "Example: towels missing, "
                "maintenance needed..."
            ),
            key=f"note_{room}",
            height=70
        )

    # -----------------------------------------------------
    # SAVE WORKING DAY
    # -----------------------------------------------------

    st.divider()

    st.subheader("💾 Save Working Day")

    st.write(
        "Save today's cleaning information "
        "to the database."
    )

    if st.button(
        "💾 Save Today's Work",
        use_container_width=True
    ):

        try:

            notes = {
                str(room): st.session_state.room_notes[room]
                for room in range(
                    1,
                    TOTAL_ROOMS + 1
                )
                if st.session_state.room_notes[room].strip()
            }

            record = {

                "work_date":
                    today.strftime("%Y-%m-%d"),

                "current_time":
                    current_time.strftime("%H:%M"),

                "rooms_completed":
                    int(rooms_completed),

                "rooms_remaining":
                    int(rooms_remaining),

                "time_available_minutes":
                    int(round(minutes_available)),

                "minutes_per_room":
                    round(
                        minutes_per_room,
                        2
                    ),

                "corridor_finished":
                    bool(corridor_finished),

                "expected_finish":
                    expected_finish_text,

                "room_notes":
                    notes

            }

            supabase.table(
                "cleaning_days"
            ).insert(
                record
            ).execute()

            st.success(
                "✅ Today's work has been "
                "saved successfully!"
            )

        except Exception as e:

            st.error(
                "❌ Could not save the data."
            )

            st.error(
                str(e)
            )


# =========================================================
# HISTORY
# =========================================================

with history_tab:

    st.subheader("📚 Working History")

    st.write(
        "All saved working days from CleanTrack Pro."
    )

    if st.button(
        "🔄 Refresh History",
        use_container_width=True
    ):

        st.rerun()

    try:

        response = (
            supabase
            .table("cleaning_days")
            .select("*")
            .order(
                "work_date",
                desc=True
            )
            .execute()
        )

        records = response.data

        if records:

            # ---------------------------------------------
            # SUMMARY
            # ---------------------------------------------

            df = pd.DataFrame(records)

            st.subheader("📊 Summary")

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Working Days",
                    len(df)
                )

            with col2:

                average_rooms = (
                    df["rooms_completed"]
                    .mean()
                )

                st.metric(
                    "Average Rooms / Day",
                    f"{average_rooms:.1f}"
                )

            with col3:

                average_time = (
                    df["minutes_per_room"]
                    .mean()
                )

                st.metric(
                    "Average Min / Room",
                    f"{average_time:.1f}"
                )

            # ---------------------------------------------
            # TABLE
            # ---------------------------------------------

            st.divider()

            st.subheader(
                "📅 Previous Working Days"
            )

            display_columns = [
                "work_date",
                "current_time",
                "rooms_completed",
                "rooms_remaining",
                "time_available_minutes",
                "minutes_per_room",
                "corridor_finished",
                "expected_finish"
            ]

            available_columns = [
                column
                for column in display_columns
                if column in df.columns
            ]

            st.dataframe(
                df[available_columns],
                use_container_width=True,
                hide_index=True
            )

            # ---------------------------------------------
            # NOTES
            # ---------------------------------------------

            st.divider()

            st.subheader(
                "📝 Room Notes"
            )

            for record in records:

                work_date = record.get(
                    "work_date",
                    "Unknown date"
                )

                notes = record.get(
                    "room_notes",
                    {}
                )

                if notes:

                    with st.expander(
                        f"📅 {work_date}"
                    ):

                        for room, note in notes.items():

                            st.write(
                                f"**Room {room}:** "
                                f"{note}"
                            )

            # ---------------------------------------------
            # DOWNLOAD CSV
            # ---------------------------------------------

            st.divider()

            st.subheader(
                "📥 Export Data"
            )

            # Convert room notes to text
            export_df = df.copy()

            if "room_notes" in export_df.columns:

                export_df["room_notes"] = (
                    export_df["room_notes"]
                    .apply(str)
                )

            csv_data = export_df.to_csv(
                index=False
            )

            st.download_button(
                label="📥 Download History as CSV",
                data=csv_data,
                file_name=(
                    "cleantrack_history.csv"
                ),
                mime="text/csv",
                use_container_width=True
            )

        else:

            st.info(
                "📭 No working days have been "
                "saved yet."
            )

    except Exception as e:

        st.error(
            "❌ Could not load the history."
        )

        st.error(
            str(e)
        )