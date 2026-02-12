import streamlit as st
from google import genai
import json
import time
from github import Github
from PIL import Image
from contextlib import redirect_stdout
import io

# --- 1. COMPACT WHITE UI (NO SCROLL) ---
st.set_page_config(page_title="Nexus Omni", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Google Sans', sans-serif; 
        background-color: #FFFFFF; 
        color: #1f1f1f; 
    }
    
    /* Force compact layout */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 0rem !important;
    }

    .google-header {
        font-size: 2.5rem;
        font-weight: 500;
        text-align: center;
        background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #5f6368;
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Clean Sidebar - No Dividers */
    [data-testid="stSidebar"] { 
        background-color: #f8f9fa !important; 
        border-right: 1px solid #e0e0e0 !important;
    }
    
    /* Chat Container Height for 1-Page fit */
    .stChatMessage {
        margin-bottom: 4px !important;
        padding: 4px !important;
    }

    /* Seamless Input Bar */
    .stChatInputContainer { 
        background-color: #FFFFFF !important;
        border: 1px solid #dadce0 !important;
        border-radius: 24px !important;
        margin-bottom: 5px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE AUTH ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except Exception as e:
    st.error("📡 Neural Core Offline.")
    st.stop()

# --- 3. SEAMLESS SIDEBAR (NO WALLS) ---
with st.sidebar:
    st.markdown("<h4 style='color:#4285F4; margin-top:0;'>Nexus Omni</h4>", unsafe_allow_html=True)
    
    usage_mode = st.radio("Mode", ["Standard Chat", "Live Web Search", "Python Lab"], label_visibility="collapsed")
    
    st.markdown("<p style='color:#5f6368; font-size:0.75rem; margin-top:10px; margin-bottom:2px;'>PROJECT SELECTION</p>", unsafe_allow_html=True)
    project_folder = st.selectbox("Project", ["General", "Coding", "Personal", "Research"], label_visibility="collapsed")
    
    # Memory Sync
    memory_filename = f"memory_{project_folder.lower()}.json"
    if 'memory_data' not in st.session_state or st.session_state.get('last_folder') != project_folder:
        try:
            mem_file = repo.get_contents(memory_filename)
            st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
        except:
            st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
        st.session_state.last_folder = project_folder

    # Removed '---' divider to allow seamless flow
    uploaded_img = st.file_uploader("Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    audio_file = st.audio_input("Audio", label_visibility="collapsed")

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">How can I help you today, Adil?</div>', unsafe_allow_html=True)

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Centered Chat Flow with vertical constraint
col1, col_main, col2 = st.columns([1, 5, 1])
with col_main:
    chat_box = st.container(height=450, border=False) # Tight height for 1-page fit
    with chat_box:
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="✨" if message["role"] == "assistant" else None):
                st.markdown(message["content"])

    prompt = st.chat_input("Ask Nexus...")

    # Logic Processing
    if audio_file or uploaded_img or prompt:
        st.session_state.messages.append({"role": "user", "content": prompt if prompt else "🧬 Input Received"})
        with st.chat_message("assistant", avatar="✨"):
            try:
                contents = [f"Context: {st.session_state.memory_data.get('chat_summary','')[:300]}"]
                if uploaded_img: contents.append(Image.open(uploaded_img))
                if audio_file: contents.append({"inline_data": {"data": audio_file.read(), "mime_type": "audio/wav"}})
                if prompt: contents.append(prompt)

                tools = [{"google_search": {}}] if usage_mode == "Live Web Search" else None
                
                def stream_nexus():
                    for chunk in client.models.generate_content_stream(model="gemini-2.0-flash", contents=contents, config={'tools': tools}):
                        if chunk.text: yield chunk.text

                full_res = st.write_stream(stream_nexus())
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
