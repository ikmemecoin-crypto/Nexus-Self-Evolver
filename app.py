import streamlit as st
from google import genai
import json
import time
from github import Github
from PIL import Image
from contextlib import redirect_stdout
import io

# --- 1. GOOGLE LIGHT MODE - CENTRALIZED UI ---
st.set_page_config(page_title="Nexus Omni", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&family=Roboto:wght@300;400;500&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Google Sans', 'Roboto', sans-serif; 
        background-color: #FFFFFF; 
        color: #1f1f1f; 
    }
    
    .stApp { background-color: #FFFFFF; }

    /* Large Centered Header */
    .google-header {
        font-family: 'Google Sans', sans-serif;
        font-size: 4rem;
        font-weight: 500;
        text-align: center;
        background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 5vh;
    }

    .subtitle {
        text-align: center;
        color: #5f6368;
        font-size: 1.5rem;
        margin-bottom: 2rem;
    }

    /* Increased Font Sizes for Labels */
    label, .stRadio p, .stSelectbox label {
        font-size: 1.3rem !important;
        font-weight: 500 !important;
        color: #1f1f1f !important;
    }
    
    /* Centered Chat Container */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        color: #1f1f1f !important;
    }

    /* Floating Search Pill */
    .stChatInputContainer { 
        background-color: #FFFFFF !important;
        border: 1px solid #dadce0 !important;
        border-radius: 32px !important;
        box-shadow: 0 1px 6px rgba(32,33,36,.28) !important;
    }
    
    /* Control Panel Box (Below Bar) */
    .control-panel {
        background-color: #f8f9fa;
        border-radius: 24px;
        padding: 25px;
        margin-top: 20px;
        border: 1px solid #dadce0;
    }

    /* Hide Sidebar & Header */
    [data-testid="stSidebar"] { display: none; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except Exception as e:
    st.error("📡 Neural Core Offline.")
    st.stop()

# --- 3. MAIN INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">How can I help you today, Adil?</div>', unsafe_allow_html=True)

# Chat History Display
if "messages" not in st.session_state:
    st.session_state.messages = []

col_l, col_main, col_r = st.columns([1, 5, 1])

with col_main:
    # Display Messages
    for message in st.session_state.messages:
        avatar = "✨" if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(f"<div style='font-size:1.2rem;'>{message['content']}</div>", unsafe_allow_html=True)

    # The Input Bar
    prompt = st.chat_input("Ask Nexus anything...")

    # --- 4. THE BELOW-BAR CONTROL PANEL ---
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        usage_mode = st.radio("Operation Mode", ["Standard Chat", "Live Web Search", "Python Lab"])
    
    with c2:
        project_folder = st.selectbox("Project Folder", ["General", "Coding", "Personal", "Research"])
        # Memory Sync
        memory_filename = f"memory_{project_folder.lower()}.json"
        if 'memory_data' not in st.session_state or st.session_state.get('last_folder') != project_folder:
            try:
                mem_file = repo.get_contents(memory_filename)
                st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
            except:
                st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
            st.session_state.last_folder = project_folder

    with c3:
        uploaded_img = st.file_uploader("📷 Image Link", type=["jpg", "png", "jpeg"])
        audio_file = st.audio_input("🎙️ Voice Link")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Python Lab Execution
    if usage_mode == "Python Lab":
        st.divider()
        st.markdown("### 🧪 Python Sandbox")
        with st.form("lab_form"):
            code_input = st.text_area("Write Script...", value='print("Hello Adil")', height=150)
            run_submitted = st.form_submit_button("▶️ Execute Code")
        if run_submitted:
            output_buffer = io.StringIO()
            try:
                with redirect_stdout(output_buffer):
                    exec(code_input)
                st.code(output_buffer.getvalue() or "Process Complete.")
            except Exception as e:
                st.error(f"Error: {e}")
        st.stop()

    # Chat Processing Logic
    if audio_file or uploaded_img or prompt:
        display_text = prompt if prompt else "🧬 [Multimedia Received]"
        st.session_state.messages.append({"role": "user", "content": display_text})
        
        with st.chat_message("assistant", avatar="✨"):
            try:
                contents = [f"Adil's Context: {st.session_state.memory_data.get('chat_summary','')}"]
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
