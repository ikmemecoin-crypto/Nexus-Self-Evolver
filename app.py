import streamlit as st
import json
import time
from github import Github
from PIL import Image
import requests # For OpenRouter API calls
import io

# --- 1. UI CONFIG (DARK MATERIAL / NO WALLS) ---
st.set_page_config(page_title="Nexus Omni", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    html, body, [class*="st-"] { font-family: 'Google Sans', sans-serif; background-color: #131314; color: #e3e3e3; }
    .block-container { padding: 1rem 3rem !important; }
    .google-header { font-size: 2.5rem; font-weight: 500; text-align: center; background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border: none; }
    .stChatInputContainer { background-color: #1e1f20 !important; border: 1px solid #3c4043 !important; border-radius: 24px !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-PROVIDER AUTH ---
@st.cache_resource
def init_github():
    try:
        gh = Github(st.secrets["GH_TOKEN"])
        return gh.get_repo(st.secrets["GH_REPO"])
    except: return None

repo = init_github()
# OpenRouter Key from Secrets
OR_KEY = st.secrets["OPENROUTER_API_KEY"] 

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h3 style='color:white;'>Nexus Omni</h3>", unsafe_allow_html=True)
    # Pivot: Allow model switching to bypass specific provider quotas
    model_choice = st.selectbox("Engine", [
        "deepseek/deepseek-chat", 
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.1-8b-instruct:free"
    ])
    project = st.selectbox("Vault", ["General", "Coding", "Research"], label_visibility="collapsed")
    
    st.markdown("---")
    img_in = st.file_uploader("Visual Context", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    aud_in = st.audio_input("Voice Command")

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

chat_box = st.container(height=420, border=False)
with chat_box:
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
            st.markdown(m["content"])

# --- 5. ALTERNATIVE PROVIDER LOGIC (OPENROUTER) ---
prompt = st.chat_input("Command Nexus...")

if prompt or img_in or aud_in:
    user_input = prompt if prompt else "Multimedia Signal Received"
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant", avatar="✨"):
        try:
            # OpenRouter API call structure (Bypasses Google direct quota)
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OR_KEY}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": model_choice,
                    "messages": [{"role": "user", "content": user_input}]
                })
            )
            
            if response.status_code == 200:
                res_text = response.json()['choices'][0]['message']['content']
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
            else:
                st.error(f"Provider Error {response.status_code}: {response.text}")
                
        except Exception as e:
            st.error(f"Connection Glitch: {e}")
