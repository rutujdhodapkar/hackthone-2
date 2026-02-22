import streamlit as st
import json
import utils

def show():
    st.header(utils.t("🌱 Advanced Soil Improvement System"))

    data = utils.load_json()

    # =========================================================
    # 🧪 SOIL TEST INPUT
    # =========================================================

    st.subheader(utils.t("🧪 Enter Soil Test Values"))

    ph = st.number_input(utils.t("Soil pH"), 4.0, 9.5, float(data.get("ph", 6.5)))
    ec = st.number_input(utils.t("EC (dS/m)"), 0.0, 10.0, float(data.get("ec", 0.5)))
    oc = st.number_input(utils.t("Organic Carbon (%)"), 0.0, 5.0, float(data.get("oc", 0.5)))
    moisture = st.number_input(utils.t("Moisture (%)"), 0.0, 100.0, float(data.get("moisture", 20.0)))

    texture_options = ["Sandy", "Loamy", "Clay"]
    translated_texture = [utils.t(t) for t in texture_options]
    texture_idx = st.selectbox(
        utils.t("Soil Texture"),
        range(len(texture_options)),
        index=texture_options.index(data.get("texture", "Loamy")),
        format_func=lambda x: translated_texture[x]
    )
    texture = texture_options[texture_idx]

    st.markdown(f"### {utils.t('Concentration Levels')}")
    N = st.number_input(utils.t("Nitrogen (N)"), 0.0, 1000.0, float(data.get("N", 280)))
    P = st.number_input(utils.t("Phosphorus (P)"), 0.0, 1000.0, float(data.get("P", 20)))
    K = st.number_input(utils.t("Potassium (K)"), 0.0, 1000.0, float(data.get("K", 180)))

    burned_val = st.radio(utils.t("Field burned?"), [utils.t("No"), utils.t("Yes")], index=0)
    burned = "No" if burned_val == utils.t("No") else "Yes"

    # SAVE EVERYTHING
    data.update({
        "ph": ph, "ec": ec, "oc": oc, "moisture": moisture, "texture": texture,
        "N": N, "P": P, "K": K, "burned": burned
    })
    utils.save_json(data)

    # =========================================================
    # 🔍 ANALYSIS
    # =========================================================

    if st.button(utils.t("🔍 Analyze Soil Health")):

        st.subheader(utils.t("📊 Diagnosis"))

        issues = []
        chemicals = []

        if ph < 6:
            issues.append("Acidic soil")
            chemicals.append("Apply Agricultural Lime")
        elif ph > 8:
            issues.append("Alkaline soil")
            chemicals.append("Apply Gypsum + Organic Matter")

        if N < 280:
            issues.append("Nitrogen deficiency")
            chemicals.append("Urea or Ammonium Sulphate")

        if P < 20:
            issues.append("Phosphorus deficiency")
            chemicals.append("DAP or SSP")

        if K < 180:
            issues.append("Potassium deficiency")
            chemicals.append("MOP (Potash)")

        if burned == "Yes":
            chemicals.append("Biochar + Compost to restore carbon")

        if issues:
            st.warning(utils.t("⚠ Issues Found:"))
            for i in issues:
                st.write("•", utils.t(i))
        else:
            st.success(utils.t("✅ Soil looks healthy"))

        st.subheader(utils.t("💊 Recommended Treatments"))
        for c in set(chemicals):
            st.write("•", utils.t(c))

        # =====================================================
        # 🤖 AI ENHANCEMENT
        # =====================================================

        st.subheader(utils.t("🤖 AI Optimized Plan"))

        prompt = f"""
Soil Report:
pH={ph}, EC={ec}, OC={oc}, Texture={texture}
N={N}, P={P}, K={K}
Field burned={burned}

Recommend BEST fertilizers/chemicals available in India.
Return ONLY JSON:
{{
 "top_chemicals": ["name1","name2"],
 "organic_options": ["opt1","opt2"],
 "warning": "any risks",
 "expected_result": "impact"
}}
"""

        try:
            raw = utils.ask_sarvam_ai(prompt, system_prompt="You are a soil scientist powered by Sarvam AI.")
            if raw:
                start = raw.find("{")
                end = raw.rfind("}") + 1
                result = json.loads(raw[start:end])

                st.markdown(f"### {utils.t('🧪 AI Recommended Chemicals')}")
                for c in result["top_chemicals"]:
                    st.write("•", utils.t(c))

                st.markdown(f"### {utils.t('🌿 Organic Alternatives')}")
                for o in result["organic_options"]:
                    st.write("•", utils.t(o))

                st.warning(utils.t(result["warning"]))
                st.success(f"{utils.t('🌾 Expected Result')}: {utils.t(result['expected_result'])}")
                
                # PERSIST RESULTS FOR REPORT
                if "analysis_results" not in data:
                    data["analysis_results"] = {}
                data["analysis_results"].update({
                    "soil_issues": issues,
                    "soil_treatments": list(set(chemicals)),
                    "ai_soil_advice": result
                })
                utils.save_json(data)
            else:
                st.error(utils.t("AI unavailable."))
        except Exception:
            st.error(utils.t("⚠ AI unavailable at the moment."))
