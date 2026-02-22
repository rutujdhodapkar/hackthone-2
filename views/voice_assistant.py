import streamlit as st
import utils
import json
import re


def show():
    st.title(utils.t("🎙️ AI Farm Conversational Bot"))

    # ---------- SAFE INIT ---------- #
    if "lang_code" not in st.session_state:
        st.session_state.lang_code = "hi-IN"

    if "voice_messages" not in st.session_state:
        st.session_state.voice_messages = []

    if "audio_to_play" not in st.session_state:
        st.session_state.audio_to_play = None

    if "voice_turn" not in st.session_state:
        st.session_state.voice_turn = 0

    # ---------- FIRST GREETING ---------- #
    if not st.session_state.voice_messages:
        greeting = (
            "Namaste! I am your AI farming assistant. "
            "Tell me about your farm — where is it located "
            "and what crops do you grow?"
        )

        st.session_state.voice_messages.append(
            {"role": "assistant", "content": greeting}
        )

        st.session_state.audio_to_play = utils.text_to_speech(
            utils.t(greeting),
            st.session_state.lang_code,
        )

    # ---------- AUTOPLAY AUDIO ---------- #
    if st.session_state.audio_to_play:
        utils.autoplay_audio(st.session_state.audio_to_play)
        st.session_state.audio_to_play = None

    data = utils.load_json()

    # ---------- LAYOUT ---------- #
    col_chat, col_side = st.columns([3, 1])

    # =========================================================
    # SIDEBAR / PROFILE PANEL
    # =========================================================
    with col_side:

        if st.button(utils.t("🔄 Reset conversation"), width="stretch"):
            for k in ["voice_messages", "audio_to_play", "voice_turn"]:
                st.session_state.pop(k, None)
            st.rerun()

        st.subheader(utils.t("📋 Farm Profile Status"))

        # Language Selection for Voice
        st.write("---")
        st.write(f"### {utils.t('🌐 Voice Language')}")
        
        # Invert SUPPORTED_LANGUAGES to get "Name" -> "Code"
        lang_names = list(utils.SUPPORTED_LANGUAGES.keys())
        current_lang_name = next((name for name, code in utils.SUPPORTED_LANGUAGES.items() if code == st.session_state.lang_code), "Hindi")
        
        selected_lang_name = st.selectbox(
            utils.t("Select Language"),
            options=lang_names,
            index=lang_names.index(current_lang_name),
            key="voice_lang_selector"
        )
        
        new_lang_code = utils.SUPPORTED_LANGUAGES[selected_lang_name]
        if new_lang_code != st.session_state.lang_code:
            st.session_state.lang_code = new_lang_code
            st.success(f"Language set to {selected_lang_name}")
            # Optional: st.rerun() if we want immediate UI update of all translated bits
            st.rerun()

        st.write("---")

        fields = ["location", "crop", "field_size", "burned", "equipment"]

        for f in fields:
            val = data.get(f, "---")
            st.write(f"**{utils.t(f.capitalize())}:** {utils.t(str(val))}")

    # =========================================================
    # CHAT AREA
    # =========================================================
    with col_chat:

        # ----- Chat History ----- #
        for msg in st.session_state.voice_messages:

            clean_text = re.sub(
                r"<data>.*?</data>", "",
                msg["content"],
                flags=re.DOTALL
            ).strip()

            if clean_text:
                with st.chat_message(msg["role"]):
                    st.markdown(utils.t(clean_text))

        st.divider()

        st.write(utils.t("### 🎤 Speak"))

        # ----- Voice Input ----- #
        audio_data = st.audio_input(
            utils.t("Tap mic and speak"),
            key=f"voice_input_{st.session_state.voice_turn}"
        )

        if audio_data is None:
            return

        # =====================================================
        # SPEECH → TEXT
        # =====================================================
        with st.spinner(utils.t("Listening...")):
            user_text = utils.speech_to_text(
                audio_data,
                st.session_state.lang_code
            )

        if not user_text:
            st.error(utils.t("Could not hear you. Try again."))
            return

        st.session_state.voice_messages.append(
            {"role": "user", "content": user_text}
        )

        # =====================================================
        # AI RESPONSE
        # =====================================================
        with st.spinner(utils.t("AI thinking...")):

            system_prompt = f"""
You are a friendly Indian agricultural advisor bot.
Collect farm profile details via conversation.

Current known data:
{json.dumps(data)}

Rules:
• Ask ONE question at a time
• If new data found, append JSON inside <data></data>
• Be warm, simple, farmer-friendly

Required fields:
location, crop, field_size (acres), burned (Yes/No), equipment (list)
"""

            messages = [{"role": "system", "content": system_prompt}]

            for m in st.session_state.voice_messages[-6:]:
                messages.append(
                    {"role": m["role"], "content": m["content"]}
                )

            ai_resp = utils.ask_oss_chat(messages)

        if not ai_resp or ai_resp.startswith(("ERROR:", "EXCEPTION:")):
            st.error(utils.t("AI failed to respond"))
            return

        # =====================================================
        # EXTRACT STRUCTURED DATA
        # =====================================================
        match = re.search(
            r"<data>(.*?)</data>",
            ai_resp,
            re.DOTALL
        )

        if match:
            try:
                extracted = json.loads(match.group(1))
                data.update(extracted)
                utils.save_json(data)
            except Exception:
                pass

        st.session_state.voice_messages.append(
            {"role": "assistant", "content": ai_resp}
        )

        # =====================================================
        # TEXT → SPEECH
        # =====================================================
        clean_voice = re.sub(
            r"<data>.*?</data>",
            "",
            ai_resp,
            flags=re.DOTALL
        ).strip()

        st.session_state.audio_to_play = utils.text_to_speech(
            utils.t(clean_voice),
            st.session_state.lang_code
        )

        # Reset mic widget
        st.session_state.voice_turn += 1

        st.rerun()