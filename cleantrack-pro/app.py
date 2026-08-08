# =========================================================
# MATERIALS & CONSUMPTION
# =========================================================

with materials_tab:

    st.subheader("📦 Materials & Consumption")

    now = datetime.now()

    today_date = now.date()
    work_date_display = now.strftime("%d/%m/%Y")
    day_name = now.strftime("%A")

    st.info(
        f"📅 **{day_name} — {work_date_display}**"
    )

    st.caption(
        "Automatic estimated consumption based on the "
        "worker's daily cleaning activity."
    )

    # =====================================================
    # CONSUMPTION RATES
    # =====================================================

    WATER_PER_DAY = 12.0

    FLOOR_SANITARY_PER_WEEK = 1.0
    GLASS_CLEANER_PER_WEEK = 1.0
    BATHROOM_CLEANER_PER_WEEK = 1.0

    WORKING_DAYS_PER_WEEK = 5

    FLOOR_SANITARY_PER_DAY = (
        FLOOR_SANITARY_PER_WEEK
        / WORKING_DAYS_PER_WEEK
    )

    GLASS_CLEANER_PER_DAY = (
        GLASS_CLEANER_PER_WEEK
        / WORKING_DAYS_PER_WEEK
    )

    BATHROOM_CLEANER_PER_DAY = (
        BATHROOM_CLEANER_PER_WEEK
        / WORKING_DAYS_PER_WEEK
    )

    # =====================================================
    # GET TODAY'S WORK AUTOMATICALLY
    # =====================================================

    rooms_completed_today = 0

    try:

        today_response = (
            supabase
            .table("cleaning_days")
            .select(
                "rooms_completed"
            )
            .eq(
                "work_date",
                today_date.isoformat()
            )
            .order(
                "created_at",
                desc=True
            )
            .limit(1)
            .execute()
        )

        today_records = (
            today_response.data or []
        )

        if today_records:

            rooms_completed_today = int(
                today_records[0].get(
                    "rooms_completed",
                    0
                )
            )

    except Exception:

        rooms_completed_today = 0

    # =====================================================
    # AUTOMATIC CONSUMPTION
    # =====================================================

    if rooms_completed_today > 0:

        room_factor = (
            rooms_completed_today
            / TOTAL_ROOMS
        )

    else:

        # If no room record exists yet,
        # use a normal full working day.
        room_factor = 1.0


    water_consumption = (
        WATER_PER_DAY
        * room_factor
    )

    floor_sanitary_consumption = (
        FLOOR_SANITARY_PER_DAY
        * room_factor
    )

    glass_consumption = (
        GLASS_CLEANER_PER_DAY
        * room_factor
    )

    bathroom_consumption = (
        BATHROOM_CLEANER_PER_DAY
        * room_factor
    )

    # =====================================================
    # AUTOMATIC OUTPUT
    # =====================================================

    st.divider()

    st.subheader(
        "📊 Today's Estimated Consumption"
    )

    if rooms_completed_today > 0:

        st.success(
            f"🧹 Based on **{rooms_completed_today} "
            f"rooms completed today**."
        )

    else:

        st.info(
            "🧹 No completed-room record has been "
            "saved today yet. Showing the standard "
            "full-day estimate."
        )

    # -----------------------------------------------------
    # WATER
    # -----------------------------------------------------

    st.metric(
        "💧 Water",
        f"{water_consumption:.2f} L"
    )

    # -----------------------------------------------------
    # CLEANING MATERIALS
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🧴 Floor & Sanitary Cleaner",
            f"{floor_sanitary_consumption:.2f} bottle"
        )

    with col2:

        st.metric(
            "🪟 Glass Cleaner",
            f"{glass_consumption:.2f} bottle"
        )

    with col3:

        st.metric(
            "🚿 Bathroom Barrier & Floor Cleaner",
            f"{bathroom_consumption:.2f} bottle"
        )

    # =====================================================
    # DAILY STANDARD
    # =====================================================

    st.divider()

    st.subheader(
        "📌 Standard Consumption"
    )

    st.write(
        "💧 **Water:** 12 liters per working day"
    )

    st.write(
        "🧴 **Floor & Sanitary Facilities Cleaner:** "
        "1 bottle per week"
    )

    st.write(
        "🪟 **Glass Cleaner:** "
        "1 bottle per week"
    )

    st.write(
        "🚿 **Bathroom Barrier & Floor Cleaner:** "
        "1 bottle per week"
    )

    # =====================================================
    # CONSUMPTION HISTORY
    # =====================================================

    st.divider()

    st.subheader(
        "📚 Consumption History"
    )

    try:

        response = (
            supabase
            .table("cleaning_materials")
            .select("*")
            .order(
                "work_date",
                desc=False
            )
            .execute()
        )

        material_records = (
            response.data or []
        )

        if material_records:

            materials_df = pd.DataFrame(
                material_records
            )

            materials_df["work_date"] = (
                pd.to_datetime(
                    materials_df[
                        "work_date"
                    ]
                ).dt.strftime(
                    "%d/%m/%Y"
                )
            )

            display_columns = [
                "day_name",
                "work_date",
                "water_liters",
                "detergent_liters",
                "glass_cleaner_liters",
                "disinfectant_liters"
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

        else:

            st.info(
                "📭 No consumption history saved yet."
            )

    except Exception as e:

        st.error(
            "❌ Could not load consumption history."
        )

        st.code(
            str(e)
        )
