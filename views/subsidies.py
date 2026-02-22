import streamlit as st
import utils
import re
import json

def show():
    st.title(utils.t("🏛️ State Government Subsidy & Profit"))

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

    residue_tons = field_size * 1.2

    st.subheader(utils.t("👨‍🌾 Farmer Details"))
    st.write(f"**{utils.t('Crop')}**: {utils.t(crop)}")
    st.write(f"**{utils.t('Location')}**: {utils.t(location.title())}")
    st.write(f"**{utils.t('Field Size')}**: {field_size} {utils.t('acres')}")
    st.write(f"**{utils.t('Residue Generated')}**: {residue_tons:.2f} {utils.t('tons')}")
    st.write(f"**{utils.t('Burning Status')}**: {utils.t(burned)}")

    st.divider()

    # State subsidies configuration
    STATE_SUBSIDY = {
        "punjab": 2500,
        "haryana": 2000,
        "uttar pradesh": 1800,
        "mumbai": 2200,
        "maharashtra": 2200,
        "delhi": 1500
    }

    # Extract state from location string
    subsidy_per_ton = 0
    detected_state = None
    for s in STATE_SUBSIDY:
        if s in location:
            subsidy_per_ton = STATE_SUBSIDY[s]
            detected_state = s
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

    st.subheader(utils.t("🏛️ State Subsidy Details"))

    if subsidy_per_ton == 0:
        if burned == "Yes":
            st.warning(utils.t("Field was burned. No longer eligible for state subsidy."))
        else:
            st.warning(utils.t("No specific state subsidy detected for your location yet."))
            st.info(utils.t("Subsidies are currently listed for: Punjab, Haryana, UP, Delhi, and Maharashtra."))
    else:
        st.success(utils.t(f"Eligible for {detected_state.title()} State Subsidy"))
        st.write(f"**{utils.t('State Subsidy per ton')}**: ₹ {subsidy_per_ton}")
        st.write(f"**{utils.t('Total State Subsidy')}**: ₹ {total_subsidy:,.2f}")

    st.divider()

    st.subheader(utils.t("💰 Farmer Profit Summary"))
    col1, col2, col3 = st.columns(3)
    col1.metric(utils.t("Market Income"), f"₹ {market_income:,.0f}")
    col2.metric(utils.t("State Subsidy"), f"₹ {total_subsidy:,.0f}")
    col3.metric(utils.t("Total Profit"), f"₹ {total_profit:,.0f}")

    st.write(f"**{utils.t('Product being sold')}**: {utils.t(product)}")
    st.write(f"**{utils.t('Market Price per ton')}**: ₹ {price_per_ton}")

    st.divider()

    if st.button(utils.t("📄 Apply for State Subsidy"), width="stretch"):
        st.success(utils.t("Subsidy application submitted to state portal successfully! Our advisor will contact you soon."))
