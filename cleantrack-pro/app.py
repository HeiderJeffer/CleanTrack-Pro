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
# MATERIAL CONSUMPTION RATES
# =========================================================

# Normal daily consumption
WATER_PER_DAY = 12.0

# Weekly consumption
FLOOR_SANITARY_BOTTLES_PER_WEEK = 1.0
GLASS_CLEANER_BOTTLES_PER_WEEK = 1.0
BATHROOM_BARRIER_FLOOR_BOTTLES_PER_WEEK = 1.0

# 5 working days per week
WORKING_DAYS_PER_WEEK = 5

# Daily estimated bottle consumption
FLOOR_SANITARY_PER_DAY = (
    FLOOR_SANITARY_BOTTLES_PER_WEEK
    / WORKING_DAYS_PER_WEEK
)

GLASS_CLEANER_PER_DAY = (
    GLASS_CLEANER_BOTTLES_PER_WEEK
    / WORKING_DAYS_PER_WEEK
)

BATHROOM_BARRIER_FLOOR_PER_DAY = (
    BATHROOM_BARRIER_FLOOR_BOTTLES_PER_WEEK
    / WORKING_DAYS_PER_WEEK
)

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

dashboard_tab, history_tab, materials_tab = st.tabs(
    [
        "🧹 Dashboard",
        "📚 History",
        "📦 Materials & Consumption"
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
            return f"{hours}h {mins}m"

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

        notes_to_save = {}


        for room, note in (
            room_notes.items()
        ):

            if note.strip():

                notes_to_save[room] = (
                    note.strip()
                )


        day_name = now.strftime(
            "%A"
        )


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


        try:

            (
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


        st.caption(
            f"Database records found: "
            f"{len(records)}"
        )


        if len(records) == 0:

            st.warning(
                "📭 No working days were returned "
                "from the database."
            )


        else:

            df = pd.DataFrame(
                records
            )


            df.insert(
                0,
                "Day",
                range(
                    1,
                    len(df) + 1
                )
            )


            df["work_date"] = (
                pd.to_datetime(
                    df["work_date"]
                )
                .dt.strftime(
                    "%d/%m/%Y"
                )
            )


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


# =========================================================
# MATERIALS & CONSUMPTION
# =========================================================

with materials_tab:

    st.subheader(
        "📦 Materials & Consumption"
    )

    now = datetime.now()

    work_date = now.strftime(
        "%d/%m/%Y"
    )

    day_name = now.strftime(
        "%A"
    )

    st.info(
        f"📅 **{day_name} — {work_date}**"
    )


    st.caption(
        "Estimated consumption is calculated "
        "from the worker's cleaning activity."
    )


    # =====================================================
    # GET TODAY'S WORK
    # =====================================================

    today_rooms = 0

    try:

        today_response = (
            supabase
            .table(
                "cleaning_days"
            )
            .select(
                "rooms_completed"
            )
            .eq(
                "work_date",
                now.date().isoformat()
            )
            .order(
                "created_at",
                desc=True
            )
            .limit(1)
            .execute()
        )

        today_records = (
            today_response.data
            or []
        )

        if today_records:

            today_rooms = int(
                today_records[0].get(
                    "rooms_completed",
                    0
                )
            )

    except Exception:

        today_rooms = 0


    # =====================================================
    # ROOMS COMPLETED
    # =====================================================

    st.divider()

    st.subheader(
        "🛏️ Cleaning Activity"
    )

    rooms_for_consumption = st.number_input(
        "Rooms cleaned today",
        min_value=0,
        max_value=TOTAL_ROOMS,
        value=today_rooms,
        step=1
    )


    # =====================================================
    # CALCULATE CONSUMPTION
    # =====================================================

    # Consumption is based on a full working day.
    # If the worker cleans fewer than 16 rooms,
    # consumption is estimated proportionally.

    room_factor = (
        rooms_for_consumption
        / TOTAL_ROOMS
    )


    estimated_water = (
        WATER_PER_DAY
        * room_factor
    )


    estimated_floor_sanitary = (
        FLOOR_SANITARY_PER_DAY
        * room_factor
    )


    estimated_glass_cleaner = (
        GLASS_CLEANER_PER_DAY
        * room_factor
    )


    estimated_bathroom_cleaner = (
        BATHROOM_BARRIER_FLOOR_PER_DAY
        * room_factor
    )


    # =====================================================
    # CONSUMPTION DISPLAY
    # =====================================================

    st.divider()

    st.subheader(
        "📊 Estimated Daily Consumption"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "💧 Water",
            f"{estimated_water:.2f} L"
        )

        st.metric(
            "🧴 Floor & Sanitary Cleaner",
            f"{estimated_floor_sanitary:.2f} bottle"
        )


    with col2:

        st.metric(
            "🪟 Glass Cleaner",
            f"{estimated_glass_cleaner:.2f} bottle"
        )

        st.metric(
            "🚿 Bathroom Barrier & Floor Cleaner",
            f"{estimated_bathroom_cleaner:.2f} bottle"
        )


    # =====================================================
    # FULL DAY REFERENCE
    # =====================================================

    st.divider()

    st.subheader(
        "📌 Full Working Day Reference"
    )

    st.write(
        f"💧 Water: **{WATER_PER_DAY:.1f} L / day**"
    )

    st.write(
        "🧴 Floor & sanitary facilities cleaner: "
        "**1 bottle / week**"
    )

    st.write(
        "🪟 Glass cleaner: "
        "**1 bottle / week**"
    )

    st.write(
        "🚿 Bathroom barrier & floor cleaner: "
        "**1 bottle / week**"
    )


    # =====================================================
    # SAVE DAILY CONSUMPTION
    # =====================================================

    st.divider()

    st.subheader(
        "💾 Save Today's Consumption"
    )


    if st.button(
        "💾 Save Consumption",
        type="primary",
        use_container_width=True
    ):

        material_record = {

            "work_date":
                now.date().isoformat(),

            "day_name":
                day_name,

            "water_liters":
                round(
                    estimated_water,
                    2
                ),

            "detergent_liters":
                round(
                    estimated_floor_sanitary,
                    2
                ),

            "disinfectant_liters":
                round(
                    estimated_bathroom_cleaner,
                    2
                ),

            "glass_cleaner_liters":
                round(
                    estimated_glass_cleaner,
                    2
                ),

            "other_material":
                "Estimated consumption",

            "other_quantity":
                0,

            "other_unit":
                "N/A",

            "notes":
                (
                    f"Estimated from "
                    f"{rooms_for_consumption} "
                    f"rooms cleaned."
                )
        }


        try:

            (
                supabase
                .table(
                    "cleaning_materials"
                )
                .insert(
                    material_record
                )
                .execute()
            )


            st.success(
                "✅ Today's consumption "
                "was saved successfully!"
            )


        except Exception as e:

            st.error(
                "❌ Failed to save consumption."
            )

            st.code(
                str(e)
            )


    # =====================================================
    # MATERIAL HISTORY
    # =====================================================

    st.divider()

    st.subheader(
        "📚 Consumption History"
    )


    if st.button(
        "🔄 Refresh Consumption",
        use_container_width=True
    ):

        st.rerun()


    try:

        response = (
            supabase
            .table(
                "cleaning_materials"
            )
            .select("*")
            .order(
                "work_date",
                desc=False
            )
            .execute()
        )


        material_records = (
            response.data
            or []
        )


        st.caption(
            f"Database records found: "
            f"{len(material_records)}"
        )


        if material_records:

            materials_df = pd.DataFrame(
                material_records
            )


            materials_df.insert(
                0,
                "Day",
                range(
                    1,
                    len(materials_df) + 1
                )
            )


            materials_df["work_date"] = (
                pd.to_datetime(
                    materials_df[
                        "work_date"
                    ]
                )
                .dt.strftime(
                    "%d/%m/%Y"
                )
            )


            display_columns = [

                "Day",

                "day_name",

                "work_date",

                "water_liters",

                "detergent_liters",

                "disinfectant_liters",

                "glass_cleaner_liters",

                "notes"
            ]


            existing_columns = [

                column

                for column in display_columns

                if column in materials_df.columns
            ]


            st.dataframe(
                materials_df[
                    existing_columns
                ],
                use_container_width=True,
                hide_index=True
            )


            # =============================================
            # TOTAL CONSUMPTION
            # =============================================

            st.divider()

            st.subheader(
                "📊 Total Consumption"
            )


            total_water = pd.to_numeric(
                materials_df[
                    "water_liters"
                ],
                errors="coerce"
            ).sum()


            total_floor = pd.to_numeric(
                materials_df[
                    "detergent_liters"
                ],
                errors="coerce"
            ).sum()


            total_bathroom = pd.to_numeric(
                materials_df[
                    "disinfectant_liters"
                ],
                errors="coerce"
            ).sum()


            total_glass = pd.to_numeric(
                materials_df[
                    "glass_cleaner_liters"
                ],
                errors="coerce"
            ).sum()


            col1, col2 = st.columns(2)


            with col1:

                st.metric(
                    "💧 Total Water",
                    f"{total_water:.2f} L"
                )


                st.metric(
                    "🧴 Floor & Sanitary Cleaner",
                    f"{total_floor:.2f} bottles"
                )


            with col2:

                st.metric(
                    "🪟 Glass Cleaner",
                    f"{total_glass:.2f} bottles"
                )


                st.metric(
                    "🚿 Bathroom Cleaner",
                    f"{total_bathroom:.2f} bottles"
                )


            # =============================================
            # EXPORT
            # =============================================

            st.divider()

            st.subheader(
                "📥 Export Consumption Data"
            )


            csv_materials = (
                materials_df.to_csv(
                    index=False
                )
            )


            st.download_button(
                label="📥 Download Consumption CSV",
                data=csv_materials,
                file_name=(
                    "cleantrack_consumption.csv"
                ),
                mime="text/csv",
                use_container_width=True
            )


        else:

            st.info(
                "📭 No consumption records saved yet."
            )


    except Exception as e:

        st.error(
            "❌ Could not load consumption history."
        )

        st.code(
            str(e)
        )