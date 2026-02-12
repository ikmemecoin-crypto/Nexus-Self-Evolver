import streamlit as st
from google import genai
import json
import time
from github import Github
from PIL import Image
from contextlib import redirect_stdout
import io

# --- 1. COMPACT MATERIAL UI ---
st.set_page_config(page_title="Nexus Omni", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&family=Roboto:wght@300;400;500&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Google Sans', 'Roboto', sans-serif; 
        background-color: #131314; 
        color: #e3e3e3; 
    }
    
    /* Fix for hidden input: ensures content doesn't overflow */
    .block-container { padding: 1rem 2rem !important; }

    .google-header {
        font-family: 'Google Sans', sans-serif;
        font-size: 3rem;
        font-weight: 500;
        text-align: center;
        background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    .subtitle {
        text-align: center;
        color: #8e918f;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; }
    
    /* Fix for Search Bar Visibility */
    .stChatInputContainer { 
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 28px !important;
        position: fixed;
        bottom: 30px;
        z-index: 1000;
    }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE AUTH ---
@st.cache_resource
def init_connections():
    try:
        c = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return c, r
    except Exception as e:
        st.error(f"Auth Error: {e}")
        return None, None

client, repo = init_connections()
if not client: st.stop()

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h3 style='color:#e3e3e3;'>Nexus Omni</h3>", unsafe_allow_html=True)
    usage_mode = st.radio("Mode", ["Standard Chat", "Live Web Search", "Python Lab"], label_visibility="collapsed")
    
    st.markdown("<p style='color:#8e918f; font-size:0.8rem; margin-top:15px;'>CONTEXT VAULT</p>", unsafe_allow_html=True)
    project_folder = st.selectbox("Project", ["General", "Coding", "Personal", "Research"], label_visibility="collapsed")
    
    # Sync Memory
    memory_filename = f"memory_{project_folder.lower()}.json"
    if 'memory_data' not in st.session_state or st.session_state.get('last_folder') != project_folder:
        try:
            content = repo.get_contents(memory_filename)
            st.session_state.memory_data = json.loads(content.decoded_content.decode())
        except:
            st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
        st.session_state.last_folder = project_folder

    uploaded_img = st.file_uploader("Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    audio_file = st.audio_input("Voice Input")

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">Systems Optimal. Project: {project_folder}</div>', unsafe_allow_html=True)

# Feature: Python Lab
if usage_mode == "Python Lab":
    with st.form("lab_sandbox"):
        code_input = st.text_area("Python Console", value='print("Perfect Execution")', height=150)
        if st.form_submit_button("Run Code"):
            buf = io.StringIO()
            try:
                with redirect_stdout(buf):
                    exec(code_input)
                st.code(buf.getvalue() or "Executed Successfully.")
            except Exception as e:
                st.error(f"Error: {e}")
    st.stop()

# --- 5. CHAT ENGINE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main Column Layout
col_left, col_mid, col_right = st.columns([0.5, 5, 0.5])

with col_mid:
    # Fixed Chat Area
    chat_container = st.container(height=450, border=False)
    with chat_container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
                st.markdown(m["content"])

    # Input Logic
    prompt = st.chat_input("Command Nexus...")

    # Logic for Prompt OR Audio OR Image
    if prompt or uploaded_img or audio_file:
        # Prevent recursive loops
        input_text = prompt if prompt else "🧬 Multimedia Task"
        st.session_state.messages.append({"role": "user", "content": input_text})
        
        with st.chat_message("assistant", avatar="✨"):
            try:
                # Prepare Multimodal contents
                contents = [f"Summary: {st.session_state.memory_data.get('chat_summary','')[:300]}"]
                if uploaded_img: contents.append(Image.open(uploaded_img))
                if audio_file: contents.append({"inline_data": {"data": audio_file.read(), "mime_type": "audio/wav"}})
                if prompt: contents.append(prompt)

                tools = [{"google_search": {}}] if usage_mode == "Live Web Search" else None
                
                def stream_nexus():
                    for chunk in client.models.generate_content_stream(model="gemini-2.0-flash", contents=contents, config={'tools': tools}):
                        if chunk.text: yield chunk.text

                response = st.write_stream(stream_nexus())
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                st.error(f"Core Error: {e}")
