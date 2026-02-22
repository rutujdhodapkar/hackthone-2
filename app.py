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

# ---------------- THEME INJECTION ---------------- #
st.markdown("""
    <style>
    /* Only target the primary (selected) button */
    button[data-testid="stBaseButton-primary"] {
        background-color: #2E7D32 !important;
        color: white !important;
        border: none !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: #1B5E20 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

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
    "AI Assistant": "views.chat"
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

    st.sidebar.divider()
    st.sidebar.link_button(utils.t("Planty agent"), "https://leaf-agent.streamlit.app/", use_container_width=True)



    # Navbar Buttons
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
