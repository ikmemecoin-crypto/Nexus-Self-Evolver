import streamlit as st
from google import genai
import json
from github import Github
from PIL import Image

# --- 1. NEXUS ULTRA UI ---
st.set_page_config(page_title="Nexus Ultra", layout="wide")

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
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE AUTH ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except:
    st.error("📡 Neural Core Offline.")
    st.stop()

# --- 3. MEMORY ---
if 'memory_data' not in st.session_state:
    try:
        mem_file = repo.get_contents("memory.json")
        st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
    except:
        st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
    st.session_state.user_name = st.session_state.memory_data.get("user_name", "Adil")

# --- 4. SIDEBAR (VISION, VOICE, MODEL) ---
with st.sidebar:
    st.markdown("<h2 style='color:#e3e3e3;'>NEXUS OS</h2>", unsafe_allow_html=True)
    model_choice = st.selectbox("Intelligence Level", ["gemini-2.0-flash", "gemini-1.5-pro"])
    
    st.markdown("---")
    st.write("📷 **Vision Link**")
    uploaded_img = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
    if uploaded_img:
        st.image(uploaded_img, caption="Nexus Vision Active", use_container_width=True)

    st.write("🎙️ **Voice Link**")
    audio_file = st.audio_input("Speak to Nexus")
    
    if st.button("💾 Sync Memory", use_container_width=True):
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.get('messages', [])])
        st.session_state.memory_data['chat_summary'] = history[-800:]
        content = json.dumps(st.session_state.memory_data)
        f = repo.get_contents("memory.json")
        repo.update_file(f.path, "Neural Sync", content, f.sha)
        st.toast("Nexus DNA Updated")

# --- 5. CHAT ENGINE ---
st.markdown(f'<h1 class="nexus-header">Greetings, {st.session_state.user_name}</h1>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="✨" if message["role"] == "assistant" else None):
        st.markdown(message["content"])

# --- 6. MULTIMODAL PROCESSING ---
prompt = st.chat_input("Analyze this...")

if audio_file or uploaded_img or prompt:
    display_text = prompt if prompt else "🧬 [Nexus Multimodal Processing...]"
    st.session_state.messages.append({"role": "user", "content": display_text})
    with st.chat_message("user"):
        st.markdown(display_text)

    with st.chat_message("assistant", avatar="✨"):
        try:
            # Building Multimodal Payload
            contents = [f"User: {st.session_state.user_name}. Summary: {st.session_state.memory_data.get('chat_summary','')}"]
            
            if uploaded_img:
                img = Image.open(uploaded_img)
                contents.append(img)
            
            if audio_file:
                audio_bytes = audio_file.read()
                contents.append({"inline_data": {"data": audio_bytes, "mime_type": "audio/wav"}})
            
            if prompt:
                contents.append(prompt)
            else:
                contents.append("Please analyze the provided media.")

            # STREAMING ENGINE
            def stream_nexus():
                for chunk in client.models.generate_content_stream(model=model_choice, contents=contents):
                    yield chunk.text

            full_response = st.write_stream(stream_nexus())
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            if "429" in str(e):
                st.warning("⚡ API Cooling Down. Wait 30s...")
            else:
                st.error(f"Neural Error: {e}")
