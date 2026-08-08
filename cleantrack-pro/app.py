# CleanTrack Pro
# Smart Cleaning Time Tracker
# Developed by Heider Jeffer

import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import gspread
from google.oauth2.service_account import Credentials


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CleanTrack Pro",
    page_icon="🧹",
    layout="wide"
)


# =========================================================
# SETTINGS
# =========================================================

TOTAL_ROOMS = 16

END_TIME = time(13, 0)

BREAK_START = time(10, 0)
BREAK_END = time(10, 20)


# =========================================================
# GOOGLE SHEETS CONNECTION
# =========================================================

@st.cache_resource
def connect_to_google_sheets():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    sheet = client.open(
        st.secrets["google_sheet_name"]
    ).sheet1

    return sheet


# =========================================================
# INITIALIZE GOOGLE SHEETS
# =========================================================

try:

    sheet = connect_to_google_sheets()

except Exception as e:

    st.error("❌ Google Sheets connection failed.")

    st.info(
        "Please check your Streamlit Secrets and "
        "Google Sheets configuration."
    )

    st.stop()


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
    '<div class="subtitle">'
    'Smart Cleaning Time Tracker'
    '</div>',
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
    # DATE
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
            "Corridor already finished"
        )


    # -----------------------------------------------------
    # TIME CALCULATIONS
    # -----------------------------------------------------

    current_minutes = (
        current_time_input.hour * 60
        + current_time_input.minute
    )

    end_minutes = (
        END_TIME.hour * 60
        + END_TIME.minute
    )

    break_start_minutes = (
        BREAK_START.hour * 60
        + BREAK_START.minute
    )

    minutes_available = (
        end_minutes - current_minutes
    )

    # Remove 20-minute break if before 10 AM
    if current_minutes < break_start_minutes:
        minutes_available -= 20

    minutes_available = max(
        0,
        minutes_available
    )


    # -----------------------------------------------------
    # ROOMS
    # -----------------------------------------------------

    rooms_remaining = (
        TOTAL_ROOMS - rooms_completed
    )

    if rooms_remaining > 0:

        minutes_per_room = (
            minutes_available /
            rooms_remaining
        )

    else:

        minutes_per_room = 0


    # -----------------------------------------------------
    # FORMAT DURATION
    # -----------------------------------------------------

    def format_duration(minutes):

        minutes = max(
            0,
            int(round(minutes))
        )

        hours = minutes // 60
        mins = minutes % 60

        if hours > 0:

            if mins > 0:
                return f"{hours}h {mins}m"

            return f"{hours}h"

        return f"{mins}m"


    # =====================================================
    # DASHBOARD
    # =====================================================

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
            format_duration(
                minutes_available
            )
        )

    with col4:

        st.metric(
            "Minutes / Room",
            f"{minutes_per_room:.1f}"
        )


    # =====================================================
    # PROGRESS
    # =====================================================

    progress = (
        rooms_completed /
        TOTAL_ROOMS
    )

    st.progress(progress)

    st.write(
        f"**{rooms_completed} of "
        f"{TOTAL_ROOMS} rooms completed**"
    )


    # =====================================================
    # STATUS
    # =====================================================

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


    # =====================================================
    # BREAK
    # =====================================================

    st.divider()

    st.subheader("☕ Break")

    st.write("**10:00 AM – 10:20 AM**")


    # =====================================================
    # REMAINING SCHEDULE
    # =====================================================

    st.divider()

    st.subheader("🗓️ Remaining Room Plan")

    schedule_time = current_minutes

    if rooms_remaining > 0:

        for room in range(
            rooms_completed + 1,
            TOTAL_ROOMS + 1
        ):

            start_minutes = schedule_time

            end_room_minutes = (
                start_minutes +
                minutes_per_room
            )

            start_hour = int(
                start_minutes // 60
            )

            start_minute = int(
                start_minutes % 60
            )

            end_hour = int(
                end_room_minutes // 60
            )

            end_minute = int(
                end_room_minutes % 60
            )

            start_display = datetime(
                2026,
                1,
                1,
                start_hour % 24,
                start_minute
            ).strftime("%I:%M %p")

            end_display = datetime(
                2026,
                1,
                1,
                end_hour % 24,
                end_minute
            ).strftime("%I:%M %p")

            st.write(
                f"🛏️ **Room {room}:** "
                f"{start_display} → "
                f"{end_display} "
                f"(**{minutes_per_room:.1f} min**)"
            )

            schedule_time = end_room_minutes


    # =====================================================
    # EXPECTED FINISH
    # =====================================================

    if rooms_remaining > 0:

        finish_minutes = (
            current_minutes +
            (
                rooms_remaining *
                minutes_per_room
            )
        )

        finish_hour = int(
            finish_minutes // 60
        )

        finish_minute = int(
            finish_minutes % 60
        )

        expected_finish = datetime(
            2026,
            1,
            1,
            finish_hour % 24,
            finish_minute
        ).strftime("%I:%M %p")

        st.info(
            f"🎯 **Expected finish: "
            f"{expected_finish}**"
        )

    else:

        expected_finish = (
            current_time_input.strftime(
                "%I:%M %p"
            )
        )

        st.success(
            "🎉 Work completed!"
        )


    # =====================================================
    # ROOM NOTES
    # =====================================================

    st.divider()

    st.subheader("📝 Worker Notes")

    st.caption(
        "Add notes for each room."
    )

    room_notes = {}

    for room in range(
        1,
        TOTAL_ROOMS + 1
    ):

        room_notes[str(room)] = st.text_area(
            f"Room {room} – Notes",
            placeholder=(
                "Example: towels missing, "
                "maintenance needed..."
            ),
            key=f"note_{room}",
            height=70
        )


    # =====================================================
    # SAVE WORKING DAY
    # =====================================================

    st.divider()

    st.subheader("💾 Save Working Day")

    if st.button(
        "💾 Save Today's Work",
        use_container_width=True
    ):

        # Remove empty notes
        notes_to_save = {
            room: note
            for room, note in room_notes.items()
            if note.strip()
        }

        row = [

            today.strftime(
                "%d/%m/%Y"
            ),

            current_time_input.strftime(
                "%H:%M"
            ),

            int(rooms_completed),

            int(rooms_remaining),

            format_duration(
                minutes_available
            ),

            round(
                minutes_per_room,
                2
            ),

            "Yes"
            if corridor_finished
            else "No",

            expected_finish,

            str(notes_to_save)

        ]

        try:

            sheet.append_row(
                row,
                value_input_option="USER_ENTERED"
            )

            st.success(
                "✅ Today's work has been "
                "saved to Google Sheets!"
            )

        except Exception as e:

            st.error(
                "❌ Could not save the data."
            )

            st.error(str(e))


# =========================================================
# HISTORY
# =========================================================

with history_tab:

    st.subheader("📚 Working History")

    try:

        data = sheet.get_all_records()

        if data:

            df = pd.DataFrame(data)

            st.subheader("📊 Summary")

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Working Days",
                    len(df)
                )

            with col2:

                if "Rooms Completed" in df:

                    average_rooms = pd.to_numeric(
                        df["Rooms Completed"],
                        errors="coerce"
                    ).mean()

                    st.metric(
                        "Average Rooms / Day",
                        f"{average_rooms:.1f}"
                    )

            with col3:

                if "Minutes / Room" in df:

                    average_time = pd.to_numeric(
                        df["Minutes / Room"],
                        errors="coerce"
                    ).mean()

                    st.metric(
                        "Average Min / Room",
                        f"{average_time:.1f}"
                    )

            st.divider()

            st.subheader(
                "📅 Previous Working Days"
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            csv = df.to_csv(
                index=False
            )

            st.download_button(
                "📥 Download History as CSV",
                data=csv,
                file_name=(
                    "cleantrack_history.csv"
                ),
                mime="text/csv",
                use_container_width=True
            )

        else:

            st.info(
                "📭 No working days saved yet."
            )

    except Exception as e:

        st.error(
            "❌ Could not load history."
        )

        st.error(str(e))