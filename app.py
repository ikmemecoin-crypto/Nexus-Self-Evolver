import streamlit as st
from google import genai
import json
from github import Github

# --- 1. CORE CONFIG & UI ---
st.set_page_config(page_title="Nexus Ultra", layout="wide")
# (Keeping your existing CSS here...)

# --- 2. AUTH & MEMORY ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- 3. SIDEBAR (VOICE WIDGET) ---
with st.sidebar:
    st.markdown("<h1 style='color:#e3e3e3;'>Nexus</h1>", unsafe_allow_html=True)
    model_choice = st.selectbox("Neural Engine", ["gemini-2.0-flash", "gemini-1.5-pro"])
    
    st.markdown("---")
    st.write("🎙️ **Voice Command**")
    # This captures your voice as a file
    audio_file = st.audio_input("Tap to speak to Nexus")

# --- 4. MAIN INTERFACE ---
st.markdown(f'<h1 class="nexus-header">Nexus Neural Link</h1>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. MULTIMODAL PROCESSING (THE MAGIC) ---
user_query = st.chat_input("Enter a prompt here")

# Check if voice was used instead of text
if audio_file:
    # We convert the audio bytes to a format Gemini understands
    audio_bytes = audio_file.read()
    # We trigger the AI to "Listen"
    user_query = "Please transcribe and answer this voice message."

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("assistant", avatar="✨"):
        try:
            # If there's audio, we send the prompt AND the audio file
            if audio_file:
                response = client.models.generate_content(
                    model=model_choice,
                    contents=[
                        {"inline_data": {"data": audio_bytes, "mime_type": "audio/wav"}},
                        f"User: {st.session_state.user_name}. Task: {user_query}"
                    ]
                )
            else:
                # Normal text processing
                response = client.models.generate_content(
                    model=model_choice,
                    contents=user_query
                )
            
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.warning("Nexus is currently in a cooling period. Please wait.")
