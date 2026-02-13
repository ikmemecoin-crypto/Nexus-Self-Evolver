import streamlit as st
from google import genai
import json
import time
from github import Github
from PIL import Image
import io

# --- 1. UI CONFIG (SINGLE PAGE FIT) ---
st.set_page_config(page_title="Nexus Omni", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    html, body, [class*="st-"] { font-family: 'Google Sans', sans-serif; background-color: #131314; color: #e3e3e3; }
    .block-container { padding: 1rem 3rem !important; }
    .google-header { font-size: 2.5rem; font-weight: 500; text-align: center; background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #8e918f; font-size: 0.9rem; margin-bottom: 15px; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border: none; }
    .stChatInputContainer { background-color: #1e1f20 !important; border: 1px solid #3c4043 !important; border-radius: 24px !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH & RECOVERY ---
@st.cache_resource
def init_core():
    try:
        c = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return c, r
    except Exception as e:
        st.error(f"Core Offline: {e}")
        return None, None

client, repo = init_core()

# --- 3. SIDEBAR (NO WALLS) ---
with st.sidebar:
    st.markdown("<h3 style='color:white;'>Nexus Omni</h3>", unsafe_allow_html=True)
    mode = st.selectbox("Mode", ["Chat", "Search", "Lab"], label_visibility="collapsed")
    project = st.selectbox("Vault", ["General", "Coding", "Research"], label_visibility="collapsed")
    
    st.markdown("---")
    img_in = st.file_uploader("Image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    aud_in = st.audio_input("Voice")

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">Project: {project} | Status: Systems Online</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Fixed chat container for 1-page fit
chat_box = st.container(height=420, border=False)
with chat_box:
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
            st.markdown(m["content"])

# --- 5. SMART INPUT LOGIC ---
prompt = st.chat_input("Command Nexus...")

if prompt or img_in or aud_in:
    st.session_state.messages.append({"role": "user", "content": prompt if prompt else "🧬 Multimedia Task"})
    
    with st.chat_message("assistant", avatar="✨"):
        try:
            # Smart Delay to avoid 429 Quota triggers
            time.sleep(2)
            
            payload = ["Execute this for Adil:"]
            if img_in: payload.append(Image.open(img_in))
            if aud_in: payload.append({"inline_data": {"data": aud_in.read(), "mime_type": "audio/wav"}})
            if prompt: payload.append(prompt)

            def stream():
                for chunk in client.models.generate_content_stream(model="gemini-2.0-flash", contents=payload):
                    if chunk.text: yield chunk.text

            res = st.write_stream(stream())
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()
        except Exception as e:
            if "429" in str(e):
                st.warning("📡 API Quota Hit. The system is paused for 30 seconds to recover...")
                time.sleep(30)
                st.info("Recovery complete. Please try your request again.")
            else:
                st.error(f"System Error: {e}")
