import streamlit as st
from google import genai
import json
import time
from github import Github
from PIL import Image

# --- 1. NEXUS OMNI UI ENGINE ---
st.set_page_config(page_title="Nexus Omni", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; background-color: #1e1f20; color: #e3e3e3; }
    .main { background-color: #1e1f20; }
    .nexus-header {
        font-size: 2.8rem; font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    div[data-testid="stChatMessage"] {
        background-color: #2b2d2f !important; border-radius: 20px !important;
        padding: 15px !important; border: 1px solid rgba(255,255,255,0.05) !important;
    }
    .stChatInputContainer { position: fixed; bottom: 35px; border-radius: 32px !important; z-index: 1000; }
    [data-testid="stSidebar"] { background-color: #131314 !important; border-right: 1px solid #333; }
    #MainMenu, footer, header {visibility: hidden;}
    
    /* System Status Bar */
    .status-bar {
        padding: 10px; border-radius: 10px; background: #2b2d2f;
        border: 1px solid #444746; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH & CORE ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except:
    st.error("📡 Neural Core Offline.")
    st.stop()

# --- 3. PERSISTENT DNA ---
if 'memory_data' not in st.session_state:
    try:
        mem_file = repo.get_contents("memory.json")
        st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
    except:
        st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}

# --- 4. SIDEBAR (SYSTEM DASHBOARD & TOOLS) ---
with st.sidebar:
    st.markdown("<h2 style='color:#e3e3e3;'>NEXUS OMNI</h2>", unsafe_allow_html=True)
    
    # SYSTEM DASHBOARD
    st.markdown("<div class='status-bar'>🛰️ <b>System Status:</b> Operational</div>", unsafe_allow_html=True)
    usage_mode = st.radio("Operation Mode", ["Standard Chat", "Live Web Search", "Image Lab"])
    
    st.markdown("---")
    model_choice = st.selectbox("Intelligence Level", ["gemini-2.0-flash", "gemini-1.5-pro"])
    
    # TOOLS
    uploaded_img = st.file_uploader("📷 Vision Link", type=["jpg", "png", "jpeg"])
    audio_file = st.audio_input("🎙️ Voice Link")
    
    if st.button("💾 Archive DNA", use_container_width=True):
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.get('messages', [])])
        st.session_state.memory_data['chat_summary'] = history[-800:]
        content = json.dumps(st.session_state.memory_data)
        f = repo.get_contents("memory.json")
        repo.update_file(f.path, "Neural Sync", content, f.sha)
        st.toast("Nexus DNA Updated")

# --- 5. MAIN INTERFACE ---
st.markdown(f'<h1 class="nexus-header">Greetings, Adil</h1>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="✨" if message["role"] == "assistant" else None):
        st.markdown(message["content"])

# --- 6. OMNI-MODAL PROCESSING ---
prompt = st.chat_input("Command Nexus...")

if audio_file or uploaded_img or prompt:
    display_text = prompt if prompt else "🧬 [Omni-Modal Command]"
    st.session_state.messages.append({"role": "user", "content": display_text})
    with st.chat_message("user"):
        st.markdown(display_text)

    with st.chat_message("assistant", avatar="✨"):
        try:
            # Build Context
            contents = [f"User: Adil. Mode: {usage_mode}. Summary: {st.session_state.memory_data.get('chat_summary','')}"]
            
            # Feature Integration: Live Search & Image Gen Instruction
            if usage_mode == "Live Web Search":
                contents.append("Use your integrated search tools to provide the most recent information from 2026.")
            elif usage_mode == "Image Lab":
                contents.append("Act as a creative image generation assistant.")
            
            if uploaded_img:
                contents.append(Image.open(uploaded_img))
            if audio_file:
                contents.append({"inline_data": {"data": audio_file.read(), "mime_type": "audio/wav"}})
            if prompt:
                contents.append(prompt)

            # STREAMING ENGINE
            def stream_nexus():
                # Checking for Google Search Tool if Flash is used
                tools = [{"google_search": {}}] if usage_mode == "Live Web Search" else None
                
                for chunk in client.models.generate_content_stream(model=model_choice, contents=contents, config={'tools': tools}):
                    yield chunk.text

            full_response = st.write_stream(stream_nexus())
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            if "429" in str(e):
                st.warning("⚡ API Cooldown. Switching to low-power mode...")
                st.info("System will be ready in 30 seconds.")
            else:
                st.error(f"Neural Error: {e}")
