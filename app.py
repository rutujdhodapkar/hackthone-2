import streamlit as st
import importlib
import sys
import os

# Ensure the project root is in the python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import utils

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title=utils.t("AI Crop Advisor"), page_icon="🌾", layout="wide")



def ensure_session_state():
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "lang_code" not in st.session_state:
        st.session_state.lang_code = "en-IN"

ensure_session_state()

# ---------------- PAGES ---------------- #
pages = {
    "Home": "views.home",
    "Soil Intellect": "views.soil_model",
    "Eco Analysis": "views.economic_analysis",
    "Subsidies": "views.subsidies",
    "Buyers": "views.buyers",
    "Sell Residue": "views.sell",
    "AI Assistant": "views.chat",
    "Voice Model": "views.voice_assistant",
}

# ---------------- NAVIGATION ---------------- #

def main():
    # Sidebar
    st.sidebar.title(utils.t("Language"))
    lang_options = list(utils.SUPPORTED_LANGUAGES.keys())
    # Find current index
    current_lang_name = next((k for k, v in utils.SUPPORTED_LANGUAGES.items() if v == st.session_state.lang_code), "English")
    selected_lang = st.sidebar.selectbox(utils.t("Select Language"), lang_options, index=lang_options.index(current_lang_name))
    
    if utils.SUPPORTED_LANGUAGES[selected_lang] != st.session_state.lang_code:
        st.session_state.lang_code = utils.SUPPORTED_LANGUAGES[selected_lang]
        st.rerun()


    st.sidebar.link_button(utils.t("Planty agent"), "https://leaf-agent.streamlit.app/", width="stretch")

    st.sidebar.divider()
    st.sidebar.subheader(utils.t("Report Center"))
    if st.sidebar.button(utils.t("📄 Generate Full Report"), use_container_width=True):
        import report_generator
        import tempfile
        
        data = utils.load_json()
        # Mock results removed. Logic now relies on persisted analysis results.
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            report_path = report_generator.generate_pdf(data, tmp.name)
            
        with open(report_path, "rb") as f:
            st.sidebar.download_button(
                label=utils.t("⬇️ Download PDF"),
                data=f,
                file_name="Agri_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        os.unlink(report_path)



    # Navbar Buttons
    from streamlit_js_eval import streamlit_js_eval
    screen_width = streamlit_js_eval(js_expressions='window.innerWidth', key='WIDTH', want_output=True)
    user_agent = streamlit_js_eval(js_expressions='navigator.userAgent', key='UA', want_output=True)

    # Fallback/Default values
    if screen_width is None: screen_width = 1000 
    
    is_mobile = False
    if user_agent:
        mobile_keywords = ["Android", "webOS", "iPhone", "iPad", "iPod", "BlackBerry", "IEMobile", "Opera Mini"]
        is_mobile = any(keyword in user_agent for keyword in mobile_keywords)

    if screen_width < 800 or is_mobile:
        # Mobile Dropdown List
        st.info(f"{utils.t('Mobile View Enabled')}")
        selected_page = st.selectbox(
            utils.t("Menu - Choose Page"), 
            list(pages.keys()), 
            index=list(pages.keys()).index(st.session_state.page)
        )
        if selected_page != st.session_state.page:
            st.session_state.page = selected_page
            st.rerun()
    else:
        # Desktop Navbar Buttons
        cols = st.columns(len(pages))
        for i, (page_name, module_path) in enumerate(pages.items()):
            if cols[i].button(utils.t(page_name), width="stretch", type="primary" if st.session_state.page == page_name else "secondary"):
                st.session_state.page = page_name
                st.rerun()

    st.divider()

    # Load Active Page
    if st.session_state.page in pages:
        module_path = pages[st.session_state.page]
        try:
            page_module = importlib.import_module(module_path)
            page_module.show()
        except Exception as e:
            st.error(f"{utils.t('Error loading page')} {utils.t(st.session_state.page)}: {e}")
    else:
        st.error(f"{utils.t('Page')} {utils.t(st.session_state.page)} {utils.t('not found')}.")

if __name__ == "__main__":
    main()
