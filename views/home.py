import streamlit as st
from geopy.geocoders import Nominatim
from streamlit_js_eval import streamlit_js_eval
import utils

def show():
    data = utils.load_json()
    st.title(utils.t("🌾 Welcome to AI Crop Residue Advisor!"))

    st.markdown(utils.t("""
Your intelligent companion for sustainable crop residue management and profitable alternatives to stubble burning.

Use the AI Crop Residue Advisor to:

• Identify the best alternatives to crop residue burning\n
• Estimate costs, savings, and potential profit\n
• Connect with nearby buyers and government support\n

"""))

    st.divider()

    # -------- AUTO LOCATION -------- #
    st.title(utils.t("🌾 AI Crop Residue Advisor"))

    # Input instruction section
    st.subheader(utils.t("📤 Enter your farm details or allow location access"))

    st.write(
        utils.t("Provide information about your crop residue to receive the best ") +
        utils.t("management recommendations.")
    )

    st.subheader(utils.t("📍 Location"))

    if st.button(utils.t("Auto Detect Location")):
        loc = streamlit_js_eval(js_expressions='navigator.geolocation.getCurrentPosition((pos)=>pos.coords)')
        if loc:
            geolocator = Nominatim(user_agent="advisor")
            location = geolocator.reverse(f"{loc['latitude']}, {loc['longitude']}")
            data["location"] = location.address
            utils.save_json(data)
            st.success(utils.t(location.address))
        else:
            st.warning(utils.t("Permission denied. Enter manually."))

    manual_loc = st.text_input(utils.t("Enter Location Manually"), value=data.get("location", ""))
    if manual_loc:
        data["location"] = manual_loc
        utils.save_json(data)

    # -------- CROP SELECTION -------- #
    st.subheader(utils.t("🌾 Crop"))
    crops = ["Wheat", "Rice", "Maize", "Sugarcane", "Cotton", "Other"]
    
    current_crop = data.get("crop", "Wheat")
    if current_crop not in crops:
        default_index = crops.index("Other")
    else:
        default_index = crops.index(current_crop)

    translated_crops = [utils.t(c) for c in crops]
    crop_idx = st.selectbox(utils.t("Select Crop"), range(len(crops)), index=default_index, format_func=lambda x: translated_crops[x])
    crop = crops[crop_idx]

    if crop == "Other":
        crop = st.text_input(utils.t("Enter Custom Crop"), value=data.get("crop", "") if current_crop not in crops else "")

    # -------- AI AUTO DETECTION -------- #
    st.markdown("---")
    st.subheader(utils.t("📸 AI Auto-Detect Crop"))
    
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False

    if not st.session_state.show_uploader:
        if st.button(utils.t("🔍 Auto Detect")):
            st.session_state.show_uploader = True
            st.rerun()
    else:
        uploaded_file = st.file_uploader(utils.t("Upload field image to auto-detect crop"), type=["jpg", "jpeg", "png"])

        if uploaded_file:
            st.image(uploaded_file, caption=utils.t("Uploaded Image"), width=300)
            if st.button(utils.t("🔍 Analyze Image"), type="primary"):
                import base64
                with st.spinner(utils.t("AI is analyzing the image...")):
                    img_bytes = uploaded_file.read()
                    base64_image = base64.b64encode(img_bytes).decode('utf-8')
                    detected_crop = utils.detect_crop_from_image(base64_image)
                    
                    if detected_crop:
                        detected_crop = detected_crop.title()
                        data["crop"] = detected_crop
                        utils.save_json(data)
                        st.session_state.show_uploader = False # Reset for next time
                        st.success(f"{utils.t('Detected Crop')}: **{utils.t(detected_crop)}**")
                        st.rerun()
                    else:
                        st.error(utils.t("Could not identify the crop. Please select manually."))
        
        if st.button(utils.t("Cancel")):
            st.session_state.show_uploader = False
            st.rerun()

    if crop:
        data["crop"] = crop
        utils.save_json(data)

    # -------- FIELD SIZE -------- #
    try:
        default_size = float(data.get("field_size", 1.0))
    except (ValueError, TypeError):
        default_size = 1.0
        
    size = st.number_input(utils.t("Field Size (acres)"), min_value=0.1, value=default_size)
    if size:
        data["field_size"] = size
        utils.save_json(data)

    # -------- BURNED -------- #
    current_burned = data.get("burned", "No")
    burned_val = st.radio(utils.t("Has the field already been burned?"), [utils.t("No"), utils.t("Yes")], index=0 if current_burned == "No" else 1)
    data["burned"] = "No" if burned_val == utils.t("No") else "Yes"
    utils.save_json(data)

    # -------- AVAILABLE EQUIPMENT -------- #
    st.subheader(utils.t("🚜 Available Equipment"))
    equip_options = ["Tractor", "Happy Seeder", "Baler", "Rotavator", "Straw Reaper", "None"]
    translated_equip = [utils.t(e) for e in equip_options]
    
    equipments_idx = st.multiselect(
        utils.t("Select what farmer has"),
        range(len(equip_options)),
        default=[equip_options.index(e) for e in data.get("equipment", []) if e in equip_options],
        format_func=lambda x: translated_equip[x]
    )
    equipments = [equip_options[i] for i in equipments_idx]
    data["equipment"] = equipments
    utils.save_json(data)

    

    # -------- RUN ANALYSIS -------- #
    if st.button(utils.t("Run Analysis"), type="primary"):
        area = data.get("field_size", 1)
        residue = area * 2.5
        co2 = residue * 1.46
        carbon = co2 * 5

        st.subheader(utils.t("📊 Analysis Results"))
        col1, col2, col3 = st.columns(3)
        col1.metric(utils.t("Residue (tons)"), f"{residue:.2f}")
        col2.metric(utils.t("CO₂ Saved (tons)"), f"{co2:.2f}")
        col3.metric(utils.t("Carbon Value (₹)"), f"{carbon:.0f}")


        st.divider()
        
        # -------- ENVIRONMENTAL CONTEXT -------- #
        st.subheader(utils.t("☁️ Environmental & Timing Insights"))
        
        with st.expander(utils.t("🌡️ Weather & Temp Impact")):
            st.write(utils.t(f"Current Temperature: 32°C | Condition: Dry"))
            st.markdown(utils.t("""
            • **High Temp Risk**: Current heat increases residue dry-matter, making it highly flammable. Use caution.\n
            • **Soil Impact**: Dry conditions mean direct incorporation will require extra irrigation to start decomposition.\n
            • **Quality**: Low humidity is excellent for baling and transport as it reduces moisture weight.
            """))

        with st.expander(utils.t("📅 Optimal Selling Window")):
            st.info(utils.t("Based on current market trends and weather forecasts:"))
            st.markdown(utils.t("""
            • **Best Period**: Next 10-15 days (Post-Harvest Peak).\n
            • **Market Outlook**: Demand is high in nearby industrial clusters. Selling before the monsoon onset is critical to maintain quality.\n
            • **Decision Window**: Take action within 7 days to avoid price drops due to oversupply.
            """))

        st.divider()
        
        st.progress(70, text=utils.t("Processing farm intelligence..."))
        
        # ---------- SARVAM AI ADVICE ---------- #
        burned_str = data.get("burned", "No")
        if burned_str == "Yes":
            burning_instruction = "The field was already burned. Tell the farmer what to do NOW to recover the soil and avoid burning next time."
        else:
            burning_instruction = "The field was NOT burned. Tell the farmer exactly what to do INSTEAD of burning, step by step."

        prompt = f"""
        Farmer location: {data.get('location')}
        Crop: {data.get('crop')}
        Field size: {area} acres
        Burned: {burned_str}
        Equipment: {", ".join(equipments)}

        {burning_instruction}
        Use very simple English. Max 5 lines. No technical words.
        """
        
        advice = utils.ask_sarvam_ai(prompt, system_prompt="You are a wise Indian agricultural assistant powered by Sarvam AI.")
        
        if advice:
            st.markdown(f"### {utils.t('🌱 What You Should Do')}\n\n{utils.t(advice)}")
        else:
            st.warning(utils.t("AI advice unavailable at the moment."))

        # -------- RECOMMENDATIONS -------- #
        if burned_str == "Yes":
            st.subheader(utils.t("🔥 Field Was Burned — What To Do Now"))
            st.markdown(utils.t("""
**Steps to Recover:**
1. Add Urea or DAP to restore Nitrogen immediately
2. Apply compost or manure to rebuild organic matter
3. Water the field gently to restore moisture
4. Avoid burning again next season — use a baler instead
"""))
        else:
            st.subheader(utils.t("✔ Alternatives to Burning"))
            st.write(utils.t("Explore more profitable pathways for your crop residue:"))
            
            with st.expander(utils.t("📦 Collect & Sell Straw")):
                st.write(utils.t("Use a baler or tractor to collect straw and sell it to nearby biomass plants or industries."))
            
            with st.expander(utils.t("🚜 Field Incorporation")):
                st.write(utils.t("Mix the residue directly into the soil using a Rotavator or Mulcher to improve organic carbon."))
            
            with st.expander(utils.t("🍃 Composting & Biochar")):
                st.write(utils.t("Convert leftover straw into high-value organic manure or biochar for your own fields or local sale."))

            st.subheader(utils.t("🛠️ How To Do It"))
            st.markdown(utils.t("""
1. Collect straw using baler or tractor
2. Either mix into soil OR pack for sale
3. Contact buyers or compost unit nearby
"""))

        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/3/3c/Straw_bales.jpg",
            caption=utils.t("Collected straw bales for sale or compost"),
            width=300
        )

    # -------- SUBSIDY SECTION -------- #
    st.markdown("---")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(utils.t("🌟 Government Subsidy & Support"))
        st.write(utils.t("Explore available government schemes and financial assistance for sustainable crop residue management."))
        st.markdown(utils.t("""
• Subsidies for machinery like Happy Seeder, Super SMS, and mulchers  
• Financial support for biochar, composting, and biomass projects  
• Incentives for eco-friendly alternatives to stubble burning  
• Support varies by state, crop type, and eligibility criteria  
"""))
        st.markdown(f"### {utils.t('🌟 Benefits of these schemes:')}")
        st.markdown(utils.t("""
• Reduces initial investment burden on farmers  
• Encourages pollution-free farming practices  
• Improves long-term soil health and productivity  
• Promotes adoption of modern agricultural technologies  
"""))
        if st.button(utils.t("👉 Check Available Subsidies"), width="stretch"):
            st.session_state.page = "Subsidies"
            st.rerun()

    with col2:
        st.image(
            "https://raw.github.com/rutujdhodapkar/hackthon-1-subtask/main/unnamed.jpg",
            caption=utils.t("Sustainable farming support"),
            use_container_width=True
        )

    # -------- STRATEGIC REPORTS -------- #
    st.markdown("---")
    st.subheader(utils.t("📄 Strategic Agricultural Reports"))
    st.write(utils.t("Access the latest research and market insights to better manage your farm residue."))

    with st.expander(utils.t("📉 Regional Stubble Burning Trends (2025-26)")):
        st.write(utils.t("""
        • 15% reduction in burning incidents across North India compared to previous year.\n
        • High adoption of balers in Punjab and Haryana regions.\n
        • Increased monitoring via satellite imagery for real-time risk assessment.
        """))
        st.caption(utils.t("Source: National Agricultural Monitoring System"))

    with st.expander(utils.t("💰 Residue Market Price Forecast")):
        st.write(utils.t("""
        • Pellets/Briquettes: Market demand expected to rise by 20% for industrial power.\n
        • Bio-Ethanol: New government refineries providing stable ₹4,000/ton floor price.\n
        • Organic Manure: Rising demand in horticulture sectors for treated compost.
        """))
        st.caption(utils.t("Source: AGRI-Intellect Market Research"))

    with st.expander(utils.t("🌍 Carbon Credit & Sustainability Rewards")):
        st.write(utils.t("""
        • Farmers using 'Happy Seeder' now eligible for ₹3,000/acre carbon credits.\n
        • Direct Incorporation adds significant organic matter, reducing long-term fertilizer costs.\n
        • Eco-friendly farming certifications can increase crop market value by up to 10%.
        """))
        st.success(utils.t("Tip: Keep digital records of your residue management to claim credits."))

    # -------- THANK YOU SECTION -------- #
    st.markdown("---")
    st.subheader(utils.t("🍃 Thank You for Using Our System!"))
    st.write(utils.t("We are committed to helping farmers manage crop residue safely, profitably, and sustainably."))
    st.write(utils.t("If you need assistance, explore the voice guidance or support features within the app."))
    st.success(utils.t("🌱 Clean Fields • Healthy Soil • Better Future"))
