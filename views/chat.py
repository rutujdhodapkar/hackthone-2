import streamlit as st
import utils

def show():
    st.header(utils.t("💬 AI Farmer Chat"))
    data = utils.load_json()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(utils.t(message["content"]))

    if prompt := st.chat_input(utils.t("Ask me about your crops or field...")):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(utils.t(prompt))

        context = f"Location: {data.get('location')}, Crop: {data.get('crop')}, Size: {data.get('field_size')} acres."

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                chat_prompt = f"{context}\n\nUser Question: {prompt}"
                full_response = utils.ask_sarvam_ai(chat_prompt, system_prompt="You are a helpful AI Agricultural Advisor powered by Sarvam AI. Answer concisely.")
                
                if full_response:
                    translated_response = utils.t(full_response)
                    message_placeholder.markdown(translated_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    message_placeholder.error(utils.t("Sarvam AI did not return a response."))
            except Exception as e:
                error_msg = f"I'm sorry, I'm having trouble connecting. Error: {e}"
                message_placeholder.error(utils.t(error_msg))
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
