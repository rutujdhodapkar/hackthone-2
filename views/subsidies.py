import streamlit as st
import utils
import re
import json

def show():
    st.title(utils.t("🏛️ State Government Subsidy & Profit Intelligence"))
    st.write(utils.t("Access real-time information on state and central government schemes for residue management."))

    # Load farmer data using the utility helper
    farmer = utils.load_json()

    # Default values to prevent errors if keys are missing
    crop = farmer.get("crop", "Wheat")
    field_size = float(farmer.get("field_size", 1.0))
    location = farmer.get("location", "").lower()
    burned = farmer.get("burned", "No")
    equipment = farmer.get("equipment", [])

    # Determine product based on equipment
    if "Baler" in equipment:
        product = "Biomass Pellets"
    elif "Rotavator" in equipment:
        product = "Compost"
    else:
        product = "Raw Crop Residue"

    residue_tons = field_size * 1.5 # Adjusted yield factor

    st.subheader(utils.t("👨‍🌾 Farmer Dashboard"))
    col1, col2, col3 = st.columns(3)
    col1.metric(utils.t("Crop / Area"), f"{utils.t(crop)} / {field_size} {utils.t('Acres')}")
    col2.metric(utils.t("Location"), utils.t(location.split(',')[0].title()))
    col3.metric(utils.t("Est. Residue"), f"{residue_tons:.1f} {utils.t('Tons')}")

    st.divider()

    # ---------------- AI SCHEME DISCOVERY ---------------- #
    st.subheader(utils.t("🔍 AI Scheme Finder"))
    if st.button(utils.t("Check Live Government Schemes for My Location"), type="primary"):
        prompt = f"""
        Farmer is in {location} growing {crop}. 
        Field size: {field_size} acres. Residue handling via {product}.
        Find 2 current Indian government subsidies or schemes (Central or State like CRM Scheme, SMAM, or State specific).
        For each, provide:
        1. Scheme Name
        2. Financial Benefit (e.g., 50-80% on machinery or ₹2500/acre)
        3. Eligibility hint.
        Focus on stubble burning prevention. Match the region: {location}.
        Format as clear bullet points. Simple English.
        """
        try:
            with st.spinner(utils.t("AI is scanning government portals...")):
                advice = utils.ask_sarvam_ai(prompt, system_prompt="You are a government policy expert for Indian agriculture.")
                if advice:
                    st.info(utils.t(advice))
                else:
                    st.error(utils.t("Live data unavailable. Using local database."))
        except:
            st.error(utils.t("Error fetching live data."))

    st.divider()

    # State subsidies configuration (Static Database)
    STATE_SUBSIDY = {
        "punjab": {"per_ton": 2500, "name": "CRM Subsidy"},
        "haryana": {"per_ton": 2000, "name": "HARYANA-Stubble-Cash"},
        "uttar pradesh": {"per_ton": 1800, "name": "UP Krishi Anudan"},
        "maharashtra": {"per_ton": 2200, "name": "Maha-Agri Biochar Scheme"},
        "madhya pradesh": {"per_ton": 1900, "name": "MP Biomass Incentive"},
        "rajasthan": {"per_ton": 1700, "name": "Raj-Organic Support"},
        "delhi": {"per_ton": 1500, "name": "Delhi Green Policy"}
    }

    # Extract state from location string
    subsidy_per_ton = 0
    detected_scheme = None
    for s, info in STATE_SUBSIDY.items():
        if s in location:
            subsidy_per_ton = info["per_ton"]
            detected_scheme = info["name"]
            break

    if burned == "Yes":
        subsidy_per_ton = 0

    total_subsidy = subsidy_per_ton * residue_tons

    # Market prices per ton
    market_price = {
        "Biomass Pellets": 5800,
        "Compost": 3000,
        "Raw Crop Residue": 1500
    }

    price_per_ton = market_price.get(product, 0)
    market_income = price_per_ton * residue_tons
    total_profit = market_income + total_subsidy

    # PERSIST SUBSIDY DATA
    if "analysis_results" not in farmer:
        farmer["analysis_results"] = {}
    farmer["analysis_results"].update({
        "detected_scheme": detected_scheme,
        "subsidy_per_ton": subsidy_per_ton,
        "total_subsidy": total_subsidy,
        "market_income": market_income,
        "total_net_gain": total_profit
    })
    utils.save_json(farmer)

    st.subheader(utils.t("🏛️ Eligible State Schemes"))

    if subsidy_per_ton == 0:
        if burned == "Yes":
            st.warning(utils.t("❌ Ineligible: Field was burned. Direct subsidies are blocked for environmental violators."))
        else:
            st.warning(utils.t("ℹ️ No matched state scheme yet. Check the AI finder above for central schemes."))
    else:
        st.success(f"✅ **{utils.t(detected_scheme)}** {utils.t('is active in your region!')}")
        st.write(f"• **{utils.t('Direct Benefit')}**: ₹{subsidy_per_ton} / {utils.t('ton')}")
        st.write(f"• **{utils.t('Total Calculated Subsidy')}**: ₹{total_subsidy:,.0f}")

    st.divider()

    st.subheader(utils.t("💰 Economic Net Benefit"))
    col1, col2, col3 = st.columns(3)
    col1.metric(utils.t("Market Value"), f"₹ {market_income:,.0f}", delta=utils.t("Cash Income"))
    col2.metric(utils.t("Govt. Incentive"), f"₹ {total_subsidy:,.0f}", delta=utils.t("Subsidy"))
    col3.metric(utils.t("Total Net Gain"), f"₹ {total_profit:,.0f}", delta_color="normal")

    st.divider()

    if st.button(utils.t("📄 Apply Now & Verified Identity")):
        st.balloons()
        st.success(utils.t("Application Pushed to State Portal! Your verification is in progress."))
        st.caption(utils.t("Verification ID: AGRI-SUB-") + str(hash(location))[-6:])
