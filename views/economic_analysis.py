import streamlit as st
import json
import utils

def show():
    st.header(utils.t("💰 Advanced Economic Advisor"))
    st.write(utils.t("Detailed financial analysis for crop residue management alternatives."))

    data = utils.load_json()
    area = float(data.get("field_size", 1.0))
    crop = data.get("crop", "Wheat")
    location = data.get("location", "India")
    
    # Base yield estimates (tonnes per acre)
    yield_per_acre = 2.5 
    total_yield = yield_per_acre * area

    st.subheader(utils.t("📊 Farm Profile"))
    col1, col2, col3 = st.columns(3)
    col1.metric(utils.t("Total Area"), f"{area} {utils.t('Acres')}")
    col2.metric(utils.t("Crop Type"), utils.t(crop))
    col3.metric(utils.t("Est. Residue"), f"{total_yield:.1f} {utils.t('Tons')}")

    st.divider()

    # =========================================================
    # FINANCIAL ENGINE
    # =========================================================
    
    # Financial data per option
    # setup_cost: CAPEX (one-time)
    # labor_per_ton: Cost of manpower
    # transport_per_ton: Cost of moving material
    # value_per_ton: Market price OR fertilizer savings
    options_data = {
        "Biochar Production": {
            "setup_cost": 45000, 
            "labor_per_ton": 800,
            "transport_per_ton": 1200,
            "value_per_ton": 12000, 
            "type": "Income",
            "reason": "Highest market value per ton through carbon-rich soil enhancement."
        },
        "Pellet Manufacturing": {
            "setup_cost": 180000, 
            "labor_per_ton": 600,
            "transport_per_ton": 1000,
            "value_per_ton": 6500, 
            "type": "Income",
            "reason": "Stable demand for industrial fuel and high volume reduction."
        },
        "Compost Making": {
            "setup_cost": 8000, 
            "labor_per_ton": 1000,
            "transport_per_ton": 400,
            "value_per_ton": 3400, 
            "type": "Income",
            "reason": "Low initial investment and excellent project for local organic farming."
        },
        "Direct Incorporation": {
            "setup_cost": 35000, 
            "labor_per_ton": 1200,
            "transport_per_ton": 0, # Done on field
            "value_per_ton": 3200, 
            "type": "Savings",
            "reason": "Restores soil health directly and eliminates transportation logistics."
        }
    }

    # ROI & Break-even calculation
    st.subheader(utils.t("💹 ROI & Break-even Scenarios"))
    
    # Calculate data for the table
    table_data = []
    best_net = -1
    best_option = None

    for name, vals in options_data.items():
        total_value = vals["value_per_ton"] * total_yield
        total_opex = (vals["labor_per_ton"] + vals["transport_per_ton"]) * total_yield
        annual_net = total_value - total_opex
        
        # Calculate ROI %
        roi_pct = (annual_net / vals["setup_cost"] * 100) if vals["setup_cost"] > 0 else 0
        
        if annual_net > 0:
            break_even = vals["setup_cost"] / annual_net
            break_even_str = f"{break_even:.1f} {utils.t('Seasons')}"
        else:
            break_even_str = utils.t("N/A")

        table_data.append({
            utils.t("Strategy"): utils.t(name),
            utils.t("Labor Cost"): f"₹{vals['labor_per_ton'] * total_yield:,.0f}",
            utils.t("Transport"): f"₹{vals['transport_per_ton'] * total_yield:,.0f}",
            utils.t("Investment"): f"₹{vals['setup_cost']:,}",
            utils.t("Annual profit"): f"₹{annual_net:,.0f}",
            utils.t("ROI (%)"): f"{roi_pct:.1f}%",
            utils.t("Payback"): break_even_str
        })
        
        if annual_net > best_net:
            best_net = annual_net
            best_option = name

    # Best Method Highlight Display
    if best_option:
        st.success(f"🏆 **{utils.t('Recommended Strategy')}**: {utils.t(best_option)} — *{utils.t(options_data[best_option]['reason'])}*")

    # Professional Tabular View
    st.table(table_data)

    st.divider()

    # =========================================================
    # RESOURCE MANAGEMENT
    # =========================================================
    st.subheader(utils.t("📦 Resource Management"))
    
    with st.expander(utils.t("📉 How to Reduce Biomass Volume")):
        st.write(utils.t("Reducing the physical volume of residue can cut transport costs by up to 60%."))
        st.markdown(utils.t("""
        • **Baling**: Compresses loose straw into high-density blocks. Essential for transport over 50km.\n
        • **Chipping/Shredding**: Increases bulk density, making it easier to load into standard trailers.\n
        • **Pelletization**: The ultimate volume reduction (10:1), but requires significant initial investment.
        """))

    with st.expander(utils.t("🔥 When Burning is Essential")):
        st.warning(utils.t("Burning should always be the absolute last resort, only considered in rare crises:"))
        st.markdown(utils.t("""
        • **Severe Pest Infestation**: If the residue is heavily infested by regional pests (like Pink Bollworm) where incorporation would spread the disease.\n
        • **Extreme Sowing Window**: In rare cases with less than 3 days between crops where balers are unavailable, though 'Happy Seeder' is still preferred.\n
        • **Fungal Outbreaks**: To prevent the survival of soil-borne pathogens that unaffected by chemical treatment.
        """))

    st.divider()

    # =========================================================
    # VIDEO GUIDES (DROPDOWN)
    # =========================================================
    st.subheader(utils.t("🎬 Video Guides for Residue Management"))

    @st.dialog(utils.t("▶️ Video Guide"), width="large")
    def show_video(path, title):
        import os
        if os.path.exists(path):
            st.subheader(utils.t(title))
            st.video(path)
        else:
            st.error(utils.t("Video file not found: ") + path)

    with st.popover(utils.t("📂 Choose a Video Guide")):
        st.write(utils.t("Click a button below to watch a video tutorial:"))
        col_v1, col_v2 = st.columns(2)
        
        if col_v1.button(utils.t("Biochar"), use_container_width=True):
            show_video("biochar.mp4", "Biochar Production")
        
        if col_v2.button(utils.t("Compost"), use_container_width=True):
            show_video("compost.mp4", "Compost Making")
            
        if col_v1.button(utils.t("Pellet"), use_container_width=True):
            show_video("pellat.mp4", "Pellet Manufacturing")
            
        if col_v2.button(utils.t("Incorporation"), use_container_width=True):
            show_video("incorporation.mp4", "Direct Incorporation")

    st.divider()

    # =========================================================
    # BURNING VS SELLING COMPARISON
    # =========================================================
    st.subheader(utils.t("🔥 Burning vs. 💰 Selling Profitability"))
    
    # Mock Weather/Temp impacts
    # High temp/Dry weather increases fire risk and soil damage
    current_temp = 32 # Mocked
    weather_condition = "Dry" # Mocked
    
    # Burning Costs (Fines + Nutrient Loss + Health Impact)
    burning_fine = 2500 * area # ₹2500 per acre fine
    nutrient_loss = 1500 * total_yield # Estimated ₹1500/ton soil value loss
    total_burning_loss = burning_fine + nutrient_loss
    
    # Selling Profit (Market Price - Labor - Transport)
    market_price = 4500 * total_yield # Average price
    labor_cost = 1200 * total_yield 
    # Transport cost varies by location depth (mocked)
    transport_dist = len(location) % 50 # Mocked distance
    transport_cost = transport_dist * 20 * total_yield
    total_selling_profit = market_price - labor_cost - transport_cost
    
    col_b, col_s = st.columns(2)
    
    with col_b:
        st.markdown(f"### ❌ {utils.t('Burning Cost')}")
        st.error(f"₹{total_burning_loss:,.0f} {utils.t('Total Loss')}")
        st.write(f"- {utils.t('Env. Fines')}: ₹{burning_fine:,.0f}")
        st.write(f"- {utils.t('Soil Nutrient Loss')}: ₹{nutrient_loss:,.0f}")
        st.caption(f"{utils.t('Weather Impact')}: {utils.t(weather_condition)} ({current_temp}°C) {utils.t('increases soil degradation rate.')}")

    with col_s:
        st.markdown(f"### ✅ {utils.t('Selling Profit')}")
        st.success(f"₹{total_selling_profit:,.0f} {utils.t('Total Profit')}")
        st.write(f"- {utils.t('Gross Revenue')}: ₹{market_price:,.0f}")
        st.write(f"- {utils.t('Labor & Transport')}: ₹{(labor_cost + transport_cost):,.0f}")
        st.caption(f"{utils.t('Location Factor')}: {utils.t('Transport optimized for')} {location[:20]}...")

    if total_selling_profit > -total_burning_loss:
        st.success(f"📈 **{utils.t('Decision')}**: {utils.t('Selling is significantly more profitable than burning by')} ₹{(total_selling_profit + total_burning_loss):,.0f} {utils.t('this season.')}")

    st.divider()

    # =========================================================
    # AI STRATEGIC FORECAST
    # =========================================================
    
    st.subheader(utils.t("🤖 AI Strategic Advice"))
    
    prompt = f"""
    Farm Details: {area} acres of {crop} in {location}.
    Weather: {current_temp}C, {weather_condition}.
    Economic Data: Selling profit ₹{total_selling_profit}, Burning loss ₹{total_burning_loss}.
    
    Provide exactly 2 sentences advising the farmer on the BEST option besides burning, 
    explaining why it's better given their location and weather.
    """

    try:
        with st.spinner(utils.t("AI is calculating market forecasts...")):
            advice = utils.ask_sarvam_ai(prompt, system_prompt="You are an agricultural economist specializing in crop residue monetization.")
            if advice:
                st.info(utils.t(advice))
            else:
                st.warning(utils.t("AI advice currently unavailable."))
    except Exception as e:
        st.error(f"{utils.t('Error')}: {e}")

    st.caption(f"© {utils.t('AGRI-Intellect Financial Services')}")
