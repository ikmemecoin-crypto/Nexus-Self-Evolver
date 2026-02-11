import streamlit as st
from google import genai
import json
import time
from github import Github
from PIL import Image
from contextlib import redirect_stdout
import io

# --- 1. GOOGLE MATERIAL DESIGN (RIGHT-SIDE & BIG FONT) ---
st.set_page_config(page_title="Nexus Omni", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&family=Roboto:wght@300;400;500&display=swap');
    
    /* Global Background & A++ Font Scaling */
    html, body, [class*="st-"] { 
        font-family: 'Google Sans', 'Roboto', sans-serif; 
        background-color: #131314; 
        color: #e3e3e3; 
        font-size: 1.5rem !important; /* Huge Base Font */
    }
    
    .main { background-color: #131314; }

    /* 🚀 THE RIGHT-SIDE SIDEBAR HACK */
    [data-testid="stAppViewContainer"] {
        flex-direction: row-reverse !important;
    }
    [data-testid="stSidebar"] {
        left: auto !important;
        right: 0 !important;
        background-color: #1e1f20 !important; 
        border-left: 1px solid #3c4043 !important;
        border-right: none !important;
        width: 450px !important; /* Wider for big text */
    }

    /* A++ Header Styling */
    .google-header {
        font-family: 'Google Sans', sans-serif;
        font-size: 5rem !important;
        font-weight: 500;
        text-align: center;
        background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 5vh;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        text-align: center;
        color: #8e918f;
        font-size: 1.8rem !important;
        margin-bottom: 3rem;
    }

    /* Big Controls for A++ Visibility */
    label, .stRadio p, .stSelectbox label {
        font-size: 1.8rem !important;
        font-weight: 500 !important;
        color: #ffffff !important;
    }
    
    /* Big Chat Bubbles */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        font-size: 1.5rem !important;
    }

    /* Big Search Pill */
    .stChatInputContainer { 
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 40px !important;
        height: 80px !important;
    }
    
    .stChatInput textarea {
        font-size: 1.6rem !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH & REPO ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except Exception as e:
    st.error("📡 Connection Offline: Check Secrets.")
    st.stop()

# --- 3. SIDEBAR (CONTROLS ON RIGHT) ---
with st.sidebar:
    st.markdown("<h2 style='color:#e3e3e3; font-size: 2.5rem;'>Nexus Omni</h2>", unsafe_allow_html=True)
    
    usage_mode = st.radio("Mode", ["Standard Chat", "Live Web Search", "Python Lab"])
    
    st.markdown("---")
    project_folder = st.selectbox("Project", ["General", "Coding", "Personal", "Research"])
    
    # Persistent Memory
    memory_filename = f"memory_{project_folder.lower()}.json"
    if 'memory_data' not in st.session_state or st.session_state.get('last_folder') != project_folder:
        try:
            mem_file = repo.get_contents(memory_filename)
            st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
        except:
            st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
        st.session_state.last_folder = project_folder

    uploaded_img = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    audio_file = st.audio_input("Voice Input")

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">How can I help you today, Adil?</div>', unsafe_allow_html=True)

# Python Lab Sandbox
if usage_mode == "Python Lab":
    st.markdown("### 🧪 Python Lab")
    with st.form("lab_form"):
        code_input = st.text_area("Write Script...", value='print("Hello Adil")', height=150)
        run_submitted = st.form_submit_button("Run Code")
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

# Display centered messages
col1, col2, col3 = st.columns([0.5, 4, 0.5])
with col2:
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="✨" if message["role"] == "assistant" else None):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask Nexus...")

    if audio_file or uploaded_img or prompt:
        display_text = prompt if prompt else "🧬 Input Received"
        st.session_state.messages.append({"role": "user", "content": display_text})
        
        with st.chat_message("assistant", avatar="✨"):
            try:
                contents = [f"Context: {st.session_state.memory_data.get('chat_summary','')}"]
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
