import streamlit as st
from google import genai
import json
import time
from github import Github
from PIL import Image
from contextlib import redirect_stdout
import io

# --- 1. COMPACT GOOGLE MATERIAL UI ---
st.set_page_config(page_title="Nexus Omni", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&family=Roboto:wght@300;400;500&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Google Sans', 'Roboto', sans-serif; 
        background-color: #131314; 
        color: #e3e3e3; 
    }
    
    /* Shrink overall app padding to fit 1 page */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }

    .google-header {
        font-family: 'Google Sans', sans-serif;
        font-size: 2.8rem; /* Scaled down */
        font-weight: 500;
        text-align: center;
        background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 1vh;
    }

    .subtitle {
        text-align: center;
        color: #8e918f;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    [data-testid="stSidebar"] { 
        background-color: #1e1f20 !important; 
        padding-top: 1rem !important;
    }
    
    /* Compact Chat Bubbles */
    div[data-testid="stChatMessage"] {
        margin-bottom: 8px !important;
        padding: 5px !important;
    }

    /* Remove 'Wall' and tighten input area */
    .stChatInputContainer { 
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 24px !important;
        margin-bottom: 10px !important; /* Brought closer to controls */
    }

    /* Tighten Sidebar Elements */
    .stRadio > div { gap: 0px !important; }
    .stFileUploader { padding-top: 0px !important; }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE AUTH ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except Exception as e:
    st.error("📡 Connection Interrupted.")
    st.stop()

# --- 3. COMPACT SIDEBAR ---
with st.sidebar:
    st.markdown("<h4 style='color:#e3e3e3; margin-bottom:5px;'>Nexus Omni</h4>", unsafe_allow_html=True)
    
    usage_mode = st.radio("Mode", ["Standard Chat", "Live Web Search", "Python Lab"], label_visibility="collapsed")
    
    st.markdown("<p style='color:#8e918f; font-size:0.7rem; margin-top:10px;'>CONTEXT</p>", unsafe_allow_html=True)
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

    # No horizontal rule (divider) here to keep it one clean block
    uploaded_img = st.file_uploader("Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    audio_file = st.audio_input("Voice", label_visibility="collapsed")

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Welcome back, Adil.</div>', unsafe_allow_html=True)

# Feature: Python Lab
if usage_mode == "Python Lab":
    with st.form("lab_form"):
        code_input = st.text_area("Sandbox", value='print("Compact Mode")', height=100)
        run_submitted = st.form_submit_button("Run")
    if run_submitted:
        output_buffer = io.StringIO()
        try:
            with redirect_stdout(output_buffer):
                exec(code_input)
            st.code(output_buffer.getvalue() or "Success.")
        except Exception as e:
            st.error(f"Error: {e}")
    st.stop()

# Chat System
if "messages" not in st.session_state:
    st.session_state.messages = []

# Centered Chat Flow
col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    # We use a container with a height limit to ensure it fits 1 page
    chat_container = st.container(height=400, border=False)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="✨" if message["role"] == "assistant" else None):
                st.markdown(message["content"])

    prompt = st.chat_input("Ask Nexus...")

    if audio_file or uploaded_img or prompt:
        display_text = prompt if prompt else "🧬 Data Sent"
        st.session_state.messages.append({"role": "user", "content": display_text})
        
        with st.chat_message("assistant", avatar="✨"):
            try:
                contents = [f"Context: {st.session_state.memory_data.get('chat_summary','')[:500]}"]
                if uploaded_img: contents.append(Image.open(uploaded_img))
                if audio_file: contents.append({"inline_data": {"data": audio_file.read(), "mime_type": "audio/wav"}})
                if prompt: contents.append(prompt)

                tools = [{"google_search": {}}] if usage_mode == "Live Web Search" else None
                
                def stream_nexus():
                    for chunk in client.models.generate_content_stream(model="gemini-2.0-flash", contents=contents, config={'tools': tools}):
                        if chunk.text: yield chunk.text

                full_res = st.write_stream(stream_nexus())
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                st.rerun() # Refresh to keep within 1-page view
            except Exception as e:
                st.error(f"Neural Error: {e}")
