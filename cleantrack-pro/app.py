# CleanTrack Pro
# Smart Cleaning Time Tracker
# Developed by Heider Jeffer

import streamlit as st
from datetime import datetime, time
from supabase import create_client, Client
import pandas as pd

# =========================================================
# PAGE CONFIG
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

START_TIME = time(8, 0)
END_TIME = time(13, 0)

BREAK_START = time(10, 0)
BREAK_END = time(10, 20)

# =========================================================
# SUPABASE CONNECTION
# =========================================================

@st.cache_resource
def get_supabase() -> Client:

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)


try:

    supabase = get_supabase()

except Exception as e:

    st.error(
        "❌ Could not connect to the database."
    )

    st.write(
        "Please check your Streamlit Secrets."
    )

    st.code(str(e))

    st.stop()


# =========================================================
# HEADER
# =========================================================

st.title("🧹 CleanTrack Pro")

st.caption(
    "Smart Cleaning Time Tracker"
)

st.caption(
    "Developed by Heider Jeffer"
)


# =========================================================
# TABS
# =========================================================

dashboard_tab, history_tab = st.tabs(
    [
        "🧹 Dashboard",
        "📚 History"
    ]
)


# =========================================================
# HELPER FUNCTION
# =========================================================

def format_minutes(minutes):

    minutes = int(round(minutes))

    hours = minutes // 60
    mins = minutes % 60

    if hours > 0:

        if mins > 0:

            return (
                f"{hours}h {mins}m"
            )

        return f"{hours}h"

    return f"{mins}m"


# =========================================================
# DASHBOARD
# =========================================================

with dashboard_tab:

    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    now = datetime.now()

    work_date = now.strftime(
        "%d/%m/%Y"
    )

    st.subheader(
        "📅 Working Day"
    )

    st.info(
        f"Today: **{work_date}**"
    )


    # -----------------------------------------------------
    # INPUTS
    # -----------------------------------------------------

    st.subheader(
        "⚙️ Work Information"
    )

    col1, col2, col3 = st.columns(3)


    with col1:

        current_time = st.time_input(
            "Current time",
            value=time(8, 0)
        )


    with col2:

        rooms_completed = st.number_input(
            "Rooms completed",
            min_value=0,
            max_value=TOTAL_ROOMS,
            value=0,
            step=1
        )


    with col3:

        corridor_finished = st.checkbox(
            "Corridor finished"
        )


    # -----------------------------------------------------
    # CALCULATE MINUTES
    # -----------------------------------------------------

    current_minutes = (
        current_time.hour * 60
        + current_time.minute
    )

    end_minutes = (
        END_TIME.hour * 60
        + END_TIME.minute
    )

    break_start_minutes = (
        BREAK_START.hour * 60
        + BREAK_START.minute
    )

    break_end_minutes = (
        BREAK_END.hour * 60
        + BREAK_END.minute
    )


    # -----------------------------------------------------
    # AVAILABLE TIME
    # -----------------------------------------------------

    available_minutes = (
        end_minutes
        - current_minutes
    )


    if current_minutes < break_start_minutes:

        available_minutes -= 20


    available_minutes = max(
        0,
        available_minutes
    )


    # -----------------------------------------------------
    # ROOMS
    # -----------------------------------------------------

    rooms_remaining = (
        TOTAL_ROOMS
        - rooms_completed
    )


    # -----------------------------------------------------
    # TIME PER ROOM
    # -----------------------------------------------------

    if rooms_remaining > 0:

        minutes_per_room = (
            available_minutes
            / rooms_remaining
        )

    else:

        minutes_per_room = 0


    # =====================================================
    # CURRENT SITUATION
    # =====================================================

    st.divider()

    st.subheader(
        "📊 Current Situation"
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )


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
            format_minutes(
                available_minutes
            )
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
        rooms_completed
        / TOTAL_ROOMS
    )

    st.progress(
        progress
    )

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
            f"{minutes_per_room:.1f} "
            f"minutes per room."
        )

    elif minutes_per_room >= 10:

        st.warning(
            f"🟡 You have "
            f"{minutes_per_room:.1f} "
            f"minutes per room."
        )

    else:

        st.error(
            f"🔴 You have only "
            f"{minutes_per_room:.1f} "
            f"minutes per room."
        )


    # =====================================================
    # BREAK
    # =====================================================

    st.divider()

    st.subheader(
        "☕ Break"
    )

    st.write(
        "**10:00 AM – 10:20 AM**"
    )


    # =====================================================
    # EXPECTED FINISH
    # =====================================================

    if rooms_remaining > 0:

        finish_minutes = (
            current_minutes
            + (
                rooms_remaining
                * minutes_per_room
            )
        )

        finish_hour = int(
            finish_minutes // 60
        )

        finish_minute = int(
            finish_minutes % 60
        )


        if finish_hour < 24:

            expected_finish = datetime(
                2026,
                1,
                1,
                finish_hour,
                finish_minute
            ).strftime(
                "%I:%M %p"
            )

        else:

            expected_finish = (
                "After 1:00 PM"
            )

    else:

        expected_finish = (
            current_time.strftime(
                "%I:%M %p"
            )
        )


    st.info(
        f"🎯 **Expected finish: "
        f"{expected_finish}**"
    )


    # =====================================================
    # ROOM PLAN
    # =====================================================

    st.divider()

    st.subheader(
        "🗓️ Remaining Room Plan"
    )


    if rooms_remaining > 0:

        schedule_minutes = (
            current_minutes
        )


        for room in range(
            rooms_completed + 1,
            TOTAL_ROOMS + 1
        ):

            start_minutes = (
                schedule_minutes
            )

            end_room_minutes = (
                start_minutes
                + minutes_per_room
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
            ).strftime(
                "%I:%M %p"
            )


            end_display = datetime(
                2026,
                1,
                1,
                end_hour % 24,
                end_minute
            ).strftime(
                "%I:%M %p"
            )


            st.write(
                f"🛏️ **Room {room}:** "
                f"{start_display} → "
                f"{end_display} "
                f"({minutes_per_room:.1f} min)"
            )


            schedule_minutes = (
                end_room_minutes
            )

    else:

        st.success(
            "🏆 All rooms completed!"
        )


    # =====================================================
    # ROOM NOTES
    # =====================================================

    st.divider()

    st.subheader(
        "📝 Worker Notes"
    )

    st.caption(
        "Add notes for each room."
    )


    room_notes = {}


    for room in range(
        1,
        TOTAL_ROOMS + 1
    ):

        room_notes[str(room)] = (
            st.text_area(
                f"Room {room}",
                placeholder=(
                    "Example: towels missing, "
                    "maintenance needed..."
                ),
                key=f"room_note_{room}",
                height=70
            )
        )


    # =====================================================
    # SAVE
    # =====================================================

    st.divider()

    st.subheader(
        "💾 Save Working Day"
    )


    if st.button(
        "💾 Save Today's Work",
        type="primary",
        use_container_width=True
    ):

        # -----------------------------------------------
        # SAVE ONLY NOTES THAT CONTAIN TEXT
        # -----------------------------------------------

        notes_to_save = {}


        for room, note in (
            room_notes.items()
        ):

            if note.strip():

                notes_to_save[room] = (
                    note.strip()
                )


        # -----------------------------------------------
        # DAY NAME
        # -----------------------------------------------

        day_name = now.strftime(
            "%A"
        )


        # -----------------------------------------------
        # DATABASE RECORD
        # -----------------------------------------------

        record = {

            "day_name":
                day_name,

            "work_date":
                now.date().isoformat(),

            "work_time":
                current_time.strftime(
                    "%H:%M"
                ),

            "rooms_completed":
                int(
                    rooms_completed
                ),

            "rooms_remaining":
                int(
                    rooms_remaining
                ),

            "time_available_minutes":
                int(
                    round(
                        available_minutes
                    )
                ),

            "minutes_per_room":
                round(
                    minutes_per_room,
                    2
                ),

            "corridor_finished":
                bool(
                    corridor_finished
                ),

            "expected_finish":
                expected_finish,

            "room_notes":
                notes_to_save
        }


        # -----------------------------------------------
        # SAVE TO SUPABASE
        # -----------------------------------------------

        try:

            response = (
                supabase
                .table(
                    "cleaning_days"
                )
                .insert(
                    record
                )
                .execute()
            )


            st.success(
                "✅ Today's work was saved "
                "successfully!"
            )


        except Exception as e:

            st.error(
                "❌ Failed to save today's work."
            )

            st.code(
                str(e)
            )


# =========================================================
# HISTORY
# =========================================================

with history_tab:

    st.subheader(
        "📚 Working History"
    )


    if st.button(
        "🔄 Refresh History",
        use_container_width=True
    ):

        st.rerun()


    try:

        # -------------------------------------------------
        # GET DATA FROM SUPABASE
        # -------------------------------------------------

        response = (
            supabase
            .table(
                "cleaning_days"
            )
            .select(
                "id,"
                "day_name,"
                "work_date,"
                "work_time,"
                "rooms_completed,"
                "rooms_remaining,"
                "time_available_minutes,"
                "minutes_per_room,"
                "corridor_finished,"
                "expected_finish,"
                "room_notes"
            )
            .order(
                "work_date",
                desc=False
            )
            .execute()
        )


        records = (
            response.data
            or []
        )


        # -------------------------------------------------
        # RECORD COUNT
        # -------------------------------------------------

        st.caption(
            f"Database records found: "
            f"{len(records)}"
        )


        # -------------------------------------------------
        # NO DATA
        # -------------------------------------------------

        if len(records) == 0:

            st.warning(
                "📭 No working days were returned "
                "from the database."
            )


        else:

            df = pd.DataFrame(
                records
            )


            # =============================================
            # DAY NUMBER
            # =============================================

            df.insert(
                0,
                "Day",
                range(
                    1,
                    len(df) + 1
                )
            )


            # =============================================
            # EUROPEAN DATE
            # =============================================

            df["work_date"] = (
                pd.to_datetime(
                    df["work_date"]
                )
                .dt.strftime(
                    "%d/%m/%Y"
                )
            )


            # =============================================
            # SUMMARY
            # =============================================

            st.subheader(
                "📊 Summary"
            )


            col1, col2, col3 = (
                st.columns(3)
            )


            with col1:

                st.metric(
                    "Working Days",
                    len(df)
                )


            with col2:

                average_rooms = (
                    pd.to_numeric(
                        df[
                            "rooms_completed"
                        ],
                        errors="coerce"
                    ).mean()
                )


                st.metric(
                    "Average Rooms / Day",
                    f"{average_rooms:.1f}"
                )


            with col3:

                average_minutes = (
                    pd.to_numeric(
                        df[
                            "minutes_per_room"
                        ],
                        errors="coerce"
                    ).mean()
                )


                st.metric(
                    "Average Min / Room",
                    f"{average_minutes:.1f}"
                )


            # =============================================
            # HISTORY TABLE
            # =============================================

            st.divider()

            st.subheader(
                "📅 Previous Working Days"
            )


            display_columns = [

                "Day",

                "day_name",

                "work_date",

                "work_time",

                "rooms_completed",

                "rooms_remaining",

                "time_available_minutes",

                "minutes_per_room",

                "corridor_finished",

                "expected_finish"
            ]


            existing_columns = [

                column

                for column in display_columns

                if column in df.columns
            ]


            st.dataframe(
                df[
                    existing_columns
                ],
                use_container_width=True,
                hide_index=True
            )


            # =============================================
            # ROOM NOTES
            # =============================================

            st.divider()

            st.subheader(
                "📝 Saved Room Notes"
            )


            notes_found = False


            for record in records:

                notes = (
                    record.get(
                        "room_notes"
                    )
                    or {}
                )


                if notes:

                    notes_found = True


                    day_name = (
                        record.get(
                            "day_name",
                            ""
                        )
                    )


                    date = (
                        record.get(
                            "work_date",
                            ""
                        )
                    )


                    try:

                        date_display = (
                            pd.to_datetime(
                                date
                            ).strftime(
                                "%d/%m/%Y"
                            )
                        )

                    except Exception:

                        date_display = str(
                            date
                        )


                    with st.expander(
                        f"📅 {day_name} — "
                        f"{date_display}"
                    ):


                        if isinstance(
                            notes,
                            dict
                        ):


                            for room, note in (
                                notes.items()
                            ):

                                st.write(
                                    f"**Room {room}:** "
                                    f"{note}"
                                )


                        else:

                            st.write(
                                str(notes)
                            )


            if not notes_found:

                st.caption(
                    "No room notes have been "
                    "saved yet."
                )


            # =============================================
            # DOWNLOAD
            # =============================================

            st.divider()

            st.subheader(
                "📥 Export Data"
            )


            export_df = (
                df.copy()
            )


            if "room_notes" in (
                export_df.columns
            ):

                export_df[
                    "room_notes"
                ] = (
                    export_df[
                        "room_notes"
                    ].apply(
                        str
                    )
                )


            csv_data = (
                export_df.to_csv(
                    index=False
                )
            )


            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=(
                    "cleantrack_history.csv"
                ),
                mime="text/csv",
                use_container_width=True
            )


    except Exception as e:

        st.error(
            "❌ Could not load history."
        )

        st.code(
            str(e)
        )