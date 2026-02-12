import streamlit as st
from google import genai
import json
import time
from github import Github

# --- 1. PREMIUM GREY UI ---
st.set_page_config(page_title="Nexus OS", layout="wide")

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
    .stChatInputContainer { position: fixed; bottom: 30px; border-radius: 30px !important; z-index: 1000; }
    [data-testid="stSidebar"] { background-color: #131314 !important; border-right: 1px solid #333; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except:
    st.error("📡 Nexus Core Offline.")
    st.stop()

# --- 3. MEMORY ---
if 'memory_data' not in st.session_state:
    try:
        mem_file = repo.get_contents("memory.json")
        st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
    except:
        st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
    st.session_state.user_name = st.session_state.memory_data.get("user_name", "Adil")

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#e3e3e3; font-weight:400;'>NEXUS OS</h2>", unsafe_allow_html=True)
    model_choice = st.selectbox("Neural Engine", ["gemini-2.0-flash", "gemini-1.5-pro"])
    
    if st.button("+ Reset Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.write("🎙️ **Voice Neural Link**")
    # Using a clearer prompt for the audio input
    audio_value = st.audio_input("Speak to the Council")
    
    if st.button("💾 Archive DNA", use_container_width=True):
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.get('messages', [])])
        st.session_state.memory_data['chat_summary'] = history[-800:]
        content = json.dumps(st.session_state.memory_data)
        f = repo.get_contents("memory.json")
        repo.update_file(f.path, "Neural Sync", content, f.sha)
        st.toast("Memory Synced")

# --- 5. MAIN INTERFACE ---
st.markdown(f'<h1 class="nexus-header">Greetings, {st.session_state.user_name}</h1>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="✨" if message["role"] == "assistant" else None):
        st.markdown(message["content"])

# --- 6. VOICE & TEXT PROCESSING ---
prompt = st.chat_input("Ask Nexus anything...")

# Logic to prioritize Voice if recorded
if audio_value:
    prompt = "🎤 [Voice Message Received]"
    audio_bytes = audio_value.read()

if prompt:
    # Add User Message to History
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process AI Response with Streaming
    with st.chat_message("assistant", avatar="✨"):
        try:
            # Prepare Multi-modal Payload
            context_prompt = f"User: {st.session_state.user_name}. Summary: {st.session_state.memory_data['chat_summary']}"
            
            contents = [context_prompt]
            if audio_value:
                contents.append({"inline_data": {"data": audio_bytes, "mime_type": "audio/wav"}})
                contents.append("Transcribe this audio and reply to the user.")
            else:
                contents.append(st.session_state.messages[-1]["content"])

            # STREAMING ENGINE
            def stream_nexus():
                # Correcting the streaming call for the Client SDK
                for chunk in client.models.generate_content_stream(model=model_choice, contents=contents):
                    yield chunk.text

            full_response = st.write_stream(stream_nexus)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            if "429" in str(e):
                st.warning("⚡ API Cooling Down. Wait 30 seconds.")
            else:
                st.error(f"Neural Glitch: {e}")
