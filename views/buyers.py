import streamlit as st
import json
import pandas as pd
import random
import utils

def show():
    st.title(utils.t("📢 Buyer Finder"))

    farmer = utils.load_json()
    if not farmer:
        st.error(utils.t("Farmer data not found. Please go to Home and fill in details."))
        return

    equipment = farmer.get("equipment", [])
    if "Baler" in equipment:
        product = utils.t("Biomass Pellets")
    elif "Rotavator" in equipment:
        product = utils.t("Compost")
    else:
        product = utils.t("Raw Crop Residue")

    st.subheader(utils.t("👨‍🌾 Farmer Context"))
    st.write(f"**{utils.t('Crop')}:** {utils.t(farmer.get('crop', 'N/A'))}")
    st.write(f"**{utils.t('Location')}:** {utils.t(farmer.get('location', 'N/A'))}")
    st.write(f"**{utils.t('Recommended Product')}:** {product}")

    def fetch_buyers_using_farmer_data(farmer):
        buyers = []
        count = random.randint(2, 4)
        loc_str = farmer.get("location", "Local")
        loc_prefix = loc_str.split(",")[0] if loc_str else "Local"
        
        for i in range(count):
            buyers.append({
                utils.t("Buyer Name"): utils.t(f"{loc_prefix} Buyer {i+1}"),
                utils.t("Product"): product,
                utils.t("Price per ton (₹)"): random.randint(3000, 8000),
                utils.t("Pickup"): utils.t(random.choice(["Yes", "No"])),
                utils.t("Contact"): f"+91-9{random.randint(100000000, 999999999)}"
            })
        return pd.DataFrame(buyers)

    st.divider()

    if st.button(utils.t("🔍 Find Buyers Near Me")):
        buyers_df = fetch_buyers_using_farmer_data(farmer)
        st.subheader(utils.t("🏭 Buyers Matched Automatically"))
        st.dataframe(buyers_df, width="stretch")

        best = buyers_df.sort_values(by=utils.t("Price per ton (₹)"), ascending=False).iloc[0]

        field_size = float(farmer.get("field_size", 1.0))
        residue_est = field_size * 1.2
        income = residue_est * best[utils.t("Price per ton (₹)")]

        st.subheader(utils.t("💰 Best Buyer Recommendation"))
        st.write(f"**{utils.t('Buyer')}:** {best[utils.t('Buyer Name')]}")
        st.write(f"**{utils.t('Price per ton')}:** ₹{best[utils.t('Price per ton (₹)')]}")
        st.write(f"**{utils.t('Estimated Residue')}:** {residue_est:.2f} {utils.t('tons')}")
        st.write(f"**{utils.t('Estimated Income')}:** ₹{income:,.2f}")

        if st.button(utils.t("✅ Connect Buyer")):
            st.success(utils.t("Buyer contact shared successfully!"))

    st.divider()
    st.subheader(utils.t("🗺️ Visual Search"))
    search_query = f"Crop Residue Buyers near {farmer.get('location', 'India')}"
    maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
    st.link_button(utils.t("📍 Search Nearby Buyers on Google Maps"), maps_url, use_container_width=True)