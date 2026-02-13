import streamlit as st
from google import genai
import json
from github import Github
from PIL import Image
import io

# --- 1. STABLE UI CONFIG ---
st.set_page_config(page_title="Nexus Omni", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    html, body, [class*="st-"] { font-family: 'Google Sans', sans-serif; background-color: #131314; color: #e3e3e3; }
    
    /* Pin input bar to bottom and fix container height */
    .block-container { padding: 1rem 3rem !important; }
    .stChatInputContainer { 
        position: fixed; bottom: 30px; 
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 24px !important;
        z-index: 1000;
    }
    .google-header { font-size: 2.5rem; font-weight: 500; text-align: center; background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE CONNECTION ---
@st.cache_resource
def init_nexus():
    try:
        c = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        g = Github(st.secrets["GH_TOKEN"])
        r = g.get_repo(st.secrets["GH_REPO"])
        return c, r
    except Exception as e:
        st.error(f"Nexus Sync Failed: {e}")
        return None, None

client, repo = init_nexus()

# --- 3. SIDEBAR (VOICE & IMAGE) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Nexus Omni</h2>", unsafe_allow_html=True)
    mode = st.selectbox("Engine", ["Chat", "Search", "Lab"])
    project = st.selectbox("Vault", ["General", "Coding", "Research"])
    
    # Clean Multimedia Inputs
    st.markdown("---")
    img_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    voice_msg = st.audio_input("Voice Command")

# --- 4. MAIN CHAT INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Fixed height chat area
chat_area = st.container(height=450, border=False)
with chat_area:
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
            st.markdown(m["content"])

# --- 5. UNIFIED INPUT LOGIC ---
prompt = st.chat_input("Command Nexus...")

if prompt or img_file or voice_msg:
    user_content = prompt if prompt else "🧬 Multimedia Command"
    st.session_state.messages.append({"role": "user", "content": user_content})
    
    with st.chat_message("assistant", avatar="✨"):
        try:
            # Payload construction
            payload = ["Process this request for Adil:"]
            if img_file: payload.append(Image.open(img_file))
            if voice_msg: payload.append({"inline_data": {"data": voice_msg.read(), "mime_type": "audio/wav"}})
            if prompt: payload.append(prompt)

            def stream_response():
                for chunk in client.models.generate_content_stream(model="gemini-2.0-flash", contents=payload):
                    if chunk.text: yield chunk.text

            full_text = st.write_stream(stream_response())
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            st.rerun()
        except Exception as e:
            st.error(f"Core Error: {e}")
