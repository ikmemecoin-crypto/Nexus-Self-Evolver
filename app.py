import streamlit as st
from google import genai
import json
import time
from github import Github
from PIL import Image
from contextlib import redirect_stdout
import io

# --- 1. A++ HIGH VISIBILITY UI ---
st.set_page_config(page_title="Nexus Omni", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&family=Roboto:wght@300;400;500&display=swap');
    
    /* Global Font Scale UP */
    html, body, [class*="st-"] { 
        font-family: 'Google Sans', sans-serif; 
        background-color: #FFFFFF; 
        color: #1f1f1f;
        font-size: 1.4rem !important; /* Base Font Boost */
    }
    
    .stApp { background-color: #FFFFFF; }

    /* A++ Header */
    .google-header {
        font-size: 5rem !important; 
        font-weight: 500;
        text-align: center;
        background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 2vh;
    }

    /* Massive Sidebar Labels */
    [data-testid="stSidebar"] { 
        background-color: #f8f9fa !important; 
        width: 450px !important; /* Wider sidebar for big text */
    }
    
    section[data-testid="stSidebar"] .stText, label, .stRadio p, .stSelectbox label {
        font-size: 1.8rem !important; 
        font-weight: 600 !important;
        margin-bottom: 15px !important;
    }

    /* Big Chat Input */
    .stChatInputContainer { 
        height: 80px !important;
        border-radius: 40px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
    }
    
    .stChatInput textarea {
        font-size: 1.5rem !important;
        line-height: 1.5 !important;
    }

    /* Large Chat Messages */
    div[data-testid="stChatMessage"] div {
        font-size: 1.4rem !important;
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

# --- 3. SIDEBAR (A++ CONTROL PANEL) ---
with st.sidebar:
    st.markdown("<h1 style='color:#4285F4; font-size: 2.5rem;'>NEXUS</h1>", unsafe_allow_html=True)
    
    st.markdown("### Operation Mode")
    usage_mode = st.radio("Mode Select", ["Standard Chat", "Live Web Search", "Python Lab"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### Project Vault")
    project_folder = st.selectbox("Folder", ["General", "Coding", "Personal", "Research"], label_visibility="collapsed")
    
    # Memory Sync
    memory_filename = f"memory_{project_folder.lower()}.json"
    if 'memory_data' not in st.session_state or st.session_state.get('last_folder') != project_folder:
        try:
            mem_file = repo.get_contents(memory_filename)
            st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
        except:
            st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
        st.session_state.last_folder = project_folder

    st.markdown("---")
    uploaded_img = st.file_uploader("📷 Link Image", type=["jpg", "png", "jpeg"])
    audio_file = st.audio_input("🎙️ Link Voice")

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)

# Feature: Python Lab
if usage_mode == "Python Lab":
    st.markdown("## 🧪 Python Lab Sandbox")
    with st.form("lab_form"):
        code_input = st.text_area("Code Editor", value='print("High Visibility Mode Active")', height=200)
        run_submitted = st.form_submit_button("▶️ RUN SCRIPT")
    if run_submitted:
        output_buffer = io.StringIO()
        try:
            with redirect_stdout(output_buffer):
                exec(code_input)
            st.code(output_buffer.getvalue() or "Executed successfully.")
        except Exception as e:
            st.error(f"Error: {e}")
    st.stop()

# Chat Engine
if "messages" not in st.session_state:
    st.session_state.messages = []

# Centered Chat Flow
col_l, col_main, col_r = st.columns([0.2, 0.6, 0.2])
with col_main:
    for message in st.session_state.messages:
        avatar = "✨" if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask Nexus...")

    if audio_file or uploaded_img or prompt:
        display_text = prompt if prompt else "🧬 Multimedia Linked"
        st.session_state.messages.append({"role": "user", "content": display_text})
        
        with st.chat_message("assistant", avatar="✨"):
            try:
                contents = [f"Adil's History: {st.session_state.memory_data.get('chat_summary','')}"]
                if uploaded_img: contents.append(Image.open(uploaded_img))
                if audio_file: contents.append({"inline_data": {"data": audio_file.read(), "mime_type": "audio/wav"}})
                if prompt: contents.append(prompt)

                tools = [{"google_search": {}}] if usage_mode == "Live Web Search" else None
                
                def stream_nexus():
                    for chunk in client.models.generate_content_stream(model="gemini-2.0-flash", contents=contents, config={'tools': tools}):
                        yield chunk.text

                full_res = st.write_stream(stream_nexus())
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            except Exception as e:
                st.error(f"Neural Error: {e}")
