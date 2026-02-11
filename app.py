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
    
    /* System Status UI */
    .status-card {
        padding: 12px; border-radius: 12px; background: #2b2d2f;
        border: 1px solid #444746; margin-bottom: 15px; font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH & REPO ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except:
    st.error("📡 Neural Core Offline.")
    st.stop()

# --- 3. SIDEBAR (SYSTEM & FOLDERS) ---
with st.sidebar:
    st.markdown("<h2 style='color:#e3e3e3;'>NEXUS OMNI</h2>", unsafe_allow_html=True)
    
    # FEATURE 1: COOLDOWN TIMER & STATUS
    st.markdown("<div class='status-card'>🛰️ <b>System:</b> Operational</div>", unsafe_allow_html=True)
    if 'cooldown_end' in st.session_state and time.time() < st.session_state.cooldown_end:
        remaining = int(st.session_state.cooldown_end - time.time())
        st.warning(f"⏳ Cooldown: {remaining}s")
        time.sleep(1)
        st.rerun()

    # FEATURE 2: NEURAL PROJECT FOLDERS (CONTEXT VAULT)
    st.write("📂 **Context Vault**")
    project_folder = st.selectbox("Select Project", ["General", "Coding", "Personal", "Research"])
    memory_filename = f"memory_{project_folder.lower()}.json"

    # Load specific memory file from GitHub
    if 'memory_data' not in st.session_state or st.session_state.get('last_folder') != project_folder:
        try:
            mem_file = repo.get_contents(memory_filename)
            st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
        except:
            st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
        st.session_state.last_folder = project_folder

    st.markdown("---")
    usage_mode = st.radio("Operation Mode", ["Standard Chat", "Live Web Search", "Python Lab"])
    model_choice = st.selectbox("Neural Engine", ["gemini-2.0-flash", "gemini-1.5-pro"])
    
    uploaded_img = st.file_uploader("📷 Vision Link", type=["jpg", "png", "jpeg"])
    audio_file = st.audio_input("🎙️ Voice Link")

    if st.button("💾 Archive DNA", use_container_width=True):
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.get('messages', [])])
        st.session_state.memory_data['chat_summary'] = history[-800:]
        content = json.dumps(st.session_state.memory_data)
        try:
            f = repo.get_contents(memory_filename)
            repo.update_file(f.path, f"Neural Sync: {project_folder}", content, f.sha)
        except:
            repo.create_file(memory_filename, f"Initialize: {project_folder}", content)
        st.toast(f"Memory Saved to {project_folder}")

# --- 4. MAIN INTERFACE & LAB ---
st.markdown(f'<h1 class="nexus-header">Greetings, Adil</h1>', unsafe_allow_html=True)

# FEATURE 3: PYTHON LAB (Local Sandbox)
if usage_mode == "Python Lab":
    st.info("🧪 **Python Lab Mode**: Run local scripts without using API tokens.")
    code_input = st.text_area("Write Python Code here...", height=200)
    if st.button("Run Script"):
        try:
            exec(code_input)
        except Exception as e:
            st.error(f"Script Error: {e}")
    st.stop() # Stops standard chat from rendering in Lab mode

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="✨" if message["role"] == "assistant" else None):
        st.markdown(message["content"])

# --- 5. OMNI-MODAL PROCESSING ---
prompt = st.chat_input("Command Nexus...")

if audio_file or uploaded_img or prompt:
    display_text = prompt if prompt else "🧬 [Omni-Modal Processing]"
    st.session_state.messages.append({"role": "user", "content": display_text})
    with st.chat_message("user"):
        st.markdown(display_text)

    with st.chat_message("assistant", avatar="✨"):
        try:
            contents = [f"User: Adil. Project: {project_folder}. History: {st.session_state.memory_data.get('chat_summary','')}"]
            
            if usage_mode == "Live Web Search":
                contents.append("Perform a live web search for the latest info.")
            
            if uploaded_img:
                contents.append(Image.open(uploaded_img))
            if audio_file:
                contents.append({"inline_data": {"data": audio_file.read(), "mime_type": "audio/wav"}})
            if prompt:
                contents.append(prompt)

            # STREAMING
            tools = [{"google_search": {}}] if usage_mode == "Live Web Search" else None
            def stream_nexus():
                for chunk in client.models.generate_content_stream(model=model_choice, contents=contents, config={'tools': tools}):
                    yield chunk.text

            full_res = st.write_stream(stream_nexus())
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
        except Exception as e:
            if "429" in str(e):
                st.session_state.cooldown_end = time.time() + 30
                st.warning("⚡ API Rate Limit Reached. Cooldown initiated.")
            else:
                st.error(f"Neural Error: {e}")
