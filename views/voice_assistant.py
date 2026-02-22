import streamlit as st
import utils
import time
import json
import re

def show():
    st.title(utils.t("🎙️ AI Farm Conversational Bot"))
    
    # -------- INITIALIZE STATE -------- #
    if "voice_messages" not in st.session_state:
        st.session_state.voice_messages = []
        st.session_state.audio_to_play = None
        st.session_state.voice_turn = 0
        
        # Initial greeting
        greeting = "Namaste! I am your AI farming assistant. I'll help you set up your profile. Tell me about your farm—where is it located and what crops do you grow?"
        st.session_state.voice_messages.append({"role": "assistant", "content": greeting})
        st.session_state.audio_to_play = utils.text_to_speech(utils.t(greeting), st.session_state.lang_code)

    # Autoplay any pending audio
    if st.session_state.audio_to_play:
        utils.autoplay_audio(st.session_state.audio_to_play)
        st.session_state.audio_to_play = None

    data = utils.load_json()

    # -------- UI LAYOUT -------- #
    col1, col2 = st.columns([2, 1])

    with col2:
        if st.button(utils.t("Reset conversation"), width="stretch"):
            for key in ["voice_messages", "audio_to_play", "voice_turn"]:
                if key in st.session_state: del st.session_state[key]
            st.rerun()
        
        st.subheader(utils.t("📋 Farm Profile Status"))
        fields = ["location", "crop", "field_size", "burned", "equipment"]
        for f in fields:
            val = data.get(f, "---")
            st.write(f"**{utils.t(f.capitalize())}**: {utils.t(str(val))}")

    with col1:
        # 1. Display Chat History
        chat_container = st.container(height=400)
        with chat_container:
            for msg in st.session_state.voice_messages:
                # Hide technical tags from user
                clean_text = re.sub(r"<data>.*?</data>", "", msg["content"], flags=re.DOTALL).strip()
                if clean_text:
                    with st.chat_message(msg["role"]):
                        st.markdown(utils.t(clean_text))

        # 2. User Input
        st.divider()
        st.write(utils.t("### 🎤 Respond via Voice"))
        
        # DYNAMIC KEY to reset widget after processing
        audio_data = st.audio_input(
            utils.t("Click and speak naturally..."), 
            key=f"voice_input_{st.session_state.voice_turn}"
        )

        if audio_data is not None:
            # Transcribe
            with st.spinner(utils.t("Listening to you...")):
                user_text = utils.speech_to_text(audio_data, st.session_state.lang_code)
                
                if user_text:
                    st.session_state.voice_messages.append({"role": "user", "content": user_text})
                    
                    # Think and Extract
                    with st.spinner(utils.t("AI is processing...")):
                        system_prompt = f"""
You are a friendly Indian agricultural advisor bot. 
Task: Collect farm data via conversation.
Current Data: {json.dumps(data)}

Rules:
1. One follow-up question at a time.
2. If new info found, include it as JSON in <data></data> at the very end.
3. Be professional yet warm.

Required: location, crop, field_size (acres), burned (Yes/No), equipment (list).
"""
                        ai_resp = utils.ask_sarvam_ai(user_text, system_prompt=system_prompt)
                        
                        if ai_resp:
                            # Extract data
                            match = re.search(r"<data>(.*?)</data>", ai_resp, re.DOTALL)
                            if match:
                                try:
                                    extracted = json.loads(match.group(1))
                                    data.update(extracted)
                                    utils.save_json(data)
                                except: pass
                            
                            # Prepare for next turn
                            st.session_state.voice_messages.append({"role": "assistant", "content": ai_resp})
                            
                            # Generate TTS for next turn
                            clean_voice_text = re.sub(r"<data>.*?</data>", "", ai_resp, re.DOTALL).strip()
                            st.session_state.audio_to_play = utils.text_to_speech(utils.t(clean_voice_text), st.session_state.lang_code)
                            
                            # INCREMENT TURN to reset the audio_input widget
                            st.session_state.voice_turn += 1
                            st.rerun()
                        else:
                            st.error(utils.t("AI error. Try again."))
                else:
                    st.error(utils.t("Could not hear you properly. Try again."))
