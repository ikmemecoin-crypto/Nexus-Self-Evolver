import streamlit as st
from google import genai
import json
import time
from github import Github
from PIL import Image
from contextlib import redirect_stdout
import io

# --- 1. COMPACT MATERIAL UI (DARK) ---
st.set_page_config(page_title="Nexus Omni", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&family=Roboto:wght@300;400;500&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Google Sans', 'Roboto', sans-serif; 
        background-color: #131314; 
        color: #e3e3e3; 
    }
    
    .block-container { padding: 1rem 3rem !important; }

    .google-header {
        font-family: 'Google Sans', sans-serif;
        font-size: 2.8rem;
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
    
    /* Sidebar: Removed Walls/Dividers */
    [data-testid="stSidebar"] { 
        background-color: #1e1f20 !important; 
        border-right: none;
    }
    
    /* Smooth Chat Bubbles */
    div[data-testid="stChatMessage"] {
        margin-bottom: 12px !important;
        border-radius: 15px;
    }

    /* Seamless Search Bar */
    .stChatInputContainer { 
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 28px !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE AUTH & PERSISTENCE ---
@st.cache_resource
def get_clients():
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
    return client, repo

try:
    client, repo = get_clients()
except Exception as e:
    st.error("📡 Core Authentication Failed.")
    st.stop()

# --- 3. SIDEBAR (COMPACT & FLOWING) ---
with st.sidebar:
    st.markdown("<h4 style='color:#e3e3e3; margin-bottom:10px;'>Nexus Omni</h4>", unsafe_allow_html=True)
    
    usage_mode = st.radio("Mode", ["Standard Chat", "Live Web Search", "Python Lab"], label_visibility="collapsed")
    
    st.markdown("<p style='color:#8e918f; font-size:0.7rem; margin-top:15px; margin-bottom:2px;'>CONTEXT VAULT</p>", unsafe_allow_html=True)
    project_folder = st.selectbox("Project", ["General", "Coding", "Personal", "Research"], label_visibility="collapsed")
    
    # Persistent Memory Logic
    memory_filename = f"memory_{project_folder.lower()}.json"
    if 'memory_data' not in st.session_state or st.session_state.get('last_folder') != project_folder:
        try:
            mem_file = repo.get_contents(memory_filename)
            st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
        except:
            st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
        st.session_state.last_folder = project_folder

    # Seamless File Inputs (No Dividers)
    uploaded_img = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    audio_file = st.audio_input("Voice Input", label_visibility="collapsed")

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">Systems Optimal. Ready for {project_folder} tasks.</div>', unsafe_allow_html=True)

# Feature: Python Lab Sandbox (Optimized Execution)
if usage_mode == "Python Lab":
    with st.form("lab_form", clear_on_submit=False):
        code_input = st.text_area("Lab Console", value='print("Diagnostics: 100%")', height=150)
        run_btn = st.form_submit_button("Execute Script")
    
    if run_btn:
        output_buffer = io.StringIO()
        try:
            with redirect_stdout(output_buffer):
                exec(code_input)
            st.success("Execution Complete")
            st.code(output_buffer.getvalue() or "No output returned.")
        except Exception as e:
            st.error(f"Execution Error: {e}")
    st.stop()

# --- 5. CHAT ENGINE (ZERO GLITCH) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display centered messages in a fixed container
col_l, col_main, col_r = st.columns([1, 5, 1])
with col_main:
    chat_display = st.container(height=450, border=False)
    with chat_display:
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="✨" if message["role"] == "assistant" else None):
                st.markdown(message["content"])

    # Handle Inputs
    prompt = st.chat_input("Command Nexus...")

    if prompt or uploaded_img or audio_file:
        # Prevent duplicate message glitch
        user_content = prompt if prompt else "🧬 Multimedia Link Received"
        st.session_state.messages.append({"role": "user", "content": user_content})
        
        with st.chat_message("assistant", avatar="✨"):
            try:
                # Prepare Multimodal Payload
                contents = [f"Summary: {st.session_state.memory_data.get('chat_summary','')[:400]}"]
                if uploaded_img: contents.append(Image.open(uploaded_img))
                if audio_file: contents.append({"inline_data": {"data": audio_file.read(), "mime_type": "audio/wav"}})
                if prompt: contents.append(prompt)

                # Tool Setup
                tools = [{"google_search": {}}] if usage_mode == "Live Web Search" else None
                
                # Streaming Response
                def stream_nexus():
                    for chunk in client.models.generate_content_stream(model="gemini-2.0-flash", contents=contents, config={'tools': tools}):
                        if chunk.text: yield chunk.text

                full_response = st.write_stream(stream_nexus())
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Update memory summary (Internal Logic)
                st.session_state.memory_data['chat_summary'] = (st.session_state.memory_data['chat_summary'] + " " + full_response)[:1000]
                
                st.rerun() # Ensure the 1-page height remains stable
            except Exception as e:
                st.error(f"Neural Core Error: {e}")
