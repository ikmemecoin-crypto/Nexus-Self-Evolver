import streamlit as st
from google import genai
import json
import time
from github import Github
from PIL import Image
from contextlib import redirect_stdout
import io

# --- 1. UI RECOVERY ---
# This "expanded" setting is the key to bringing the sidebar back
st.set_page_config(page_title="Nexus Omni", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Outfit', sans-serif; 
        background-color: #1e1f20; 
        color: #e3e3e3; 
    }

    /* 🚀 THE FIX: Hide ONLY the glitchy button, NOT the whole sidebar */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Force sidebar to be visible and prevent it from hiding */
    section[data-testid="stSidebar"] {
        background-color: #131314 !important; 
        border-right: 1px solid #333;
        visibility: visible !important;
        width: 350px !important;
    }

    .main { background-color: #1e1f20; }
    .nexus-header {
        font-size: 2.8rem; font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    div[data-testid="stChatMessage"] {
        background-color: #2b2d2f !important; 
        border-radius: 20px !important;
        padding: 15px !important; 
        border: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    .stChatInputContainer { position: fixed; bottom: 35px; border-radius: 32px !important; z-index: 1000; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except Exception as e:
    st.error("📡 Neural Core Offline. Check Secrets.")
    st.stop()

# --- 3. SIDEBAR NAVIGATION ---
# This part MUST be present for the sidebar to render any content
with st.sidebar:
    st.markdown("<h2 style='color:#e3e3e3; margin-top:-30px;'>NEXUS OMNI</h2>", unsafe_allow_html=True)
    
    usage_mode = st.radio("Operation Mode", ["Standard Chat", "Live Web Search", "Python Lab"])
    
    st.markdown("---")
    project_folder = st.selectbox("Select Project", ["General", "Coding", "Personal", "Research"])
    
    # Persistent Memory Engine
    memory_filename = f"memory_{project_folder.lower()}.json"
    if 'memory_data' not in st.session_state or st.session_state.get('last_folder') != project_folder:
        try:
            mem_file = repo.get_contents(memory_filename)
            st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
        except:
            st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
        st.session_state.last_folder = project_folder

    model_choice = st.selectbox("Neural Engine", ["gemini-2.0-flash", "gemini-1.5-pro"])
    uploaded_img = st.file_uploader("📷 Vision Link", type=["jpg", "png", "jpeg"])
    audio_file = st.audio_input("🎙️ Voice Neural Link")

# --- 4. MAIN INTERFACE ---
st.markdown(f'<h1 class="nexus-header">Greetings, Adil</h1>', unsafe_allow_html=True)

# Python Lab Logic
if usage_mode == "Python Lab":
    st.info("🧪 **Python Lab**: Local code sandbox.")
    with st.form("lab_form"):
        code_input = st.text_area("Code Editor", value='print("Nexus is ready")', height=200)
        run_submitted = st.form_submit_button("▶️ Run Script")
    if run_submitted:
        st.markdown("### 🖥️ Console Output")
        output_buffer = io.StringIO()
        try:
            with redirect_stdout(output_buffer):
                exec(code_input)
            st.code(output_buffer.getvalue() or "Success: No output.")
        except Exception as e:
            st.error(f"Error: {e}")
    st.stop()

# Chat Interface Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="✨" if message["role"] == "assistant" else None):
        st.markdown(message["content"])

prompt = st.chat_input("Command Nexus...")

if audio_file or uploaded_img or prompt:
    display_text = prompt if prompt else "🧬 [Input Received]"
    st.session_state.messages.append({"role": "user", "content": display_text})
    with st.chat_message("user"):
        st.markdown(display_text)

    with st.chat_message("assistant", avatar="✨"):
        try:
            contents = [f"User: Adil. Project: {project_folder}. History: {st.session_state.memory_data.get('chat_summary','')}"]
            if uploaded_img: contents.append(Image.open(uploaded_img))
            if audio_file: contents.append({"inline_data": {"data": audio_file.read(), "mime_type": "audio/wav"}})
            if prompt: contents.append(prompt)

            tools = [{"google_search": {}}] if usage_mode == "Live Web Search" else None
            
            def stream_nexus():
                for chunk in client.models.generate_content_stream(model=model_choice, contents=contents, config={'tools': tools}):
                    yield chunk.text

            full_res = st.write_stream(stream_nexus())
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e:
            st.error(f"Neural Error: {e}")
