import streamlit as st
from google import genai
import json
import time
from github import Github

# --- 1. NEXUS-GEMINI ENGINE CONFIG ---
st.set_page_config(page_title="Nexus Ultra", layout="wide")

# CSS for the "Grey-Outfit" Aesthetic
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; background-color: #1e1f20; color: #e3e3e3; }
    .main { background-color: #1e1f20; }
    .nexus-header {
        font-size: 3rem; font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    div[data-testid="stChatMessage"] {
        background-color: #2b2d2f !important; border-radius: 24px !important;
        padding: 18px !important; margin-bottom: 12px !important;
        border: 1px solid rgba(255,255,255,0.03) !important;
    }
    .stChatInputContainer { position: fixed; bottom: 35px; border-radius: 32px !important; z-index: 1000; }
    [data-testid="stSidebar"] { background-color: #131314 !important; border-right: 1px solid #333; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH & REPO ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    g = Github(st.secrets["GH_TOKEN"])
    repo = g.get_repo(st.secrets["GH_REPO"])
except:
    st.error("📡 Nexus Core Connection Failed.")
    st.stop()

# --- 3. PERSISTENT MEMORY ---
if 'memory_data' not in st.session_state:
    try:
        mem_file = repo.get_contents("memory.json")
        st.session_state.memory_data = json.loads(mem_file.decoded_content.decode())
    except:
        st.session_state.memory_data = {"user_name": "Adil", "chat_summary": ""}
    st.session_state.user_name = st.session_state.memory_data.get("user_name", "Adil")

# --- 4. SIDEBAR (MODEL TOGGLE) ---
with st.sidebar:
    st.markdown("<h1 style='color:#e3e3e3;'>Nexus</h1>", unsafe_allow_html=True)
    
    # FEATURE 1: MODEL TOGGLE
    model_choice = st.selectbox(
        "Neural Engine",
        ["gemini-2.0-flash", "gemini-1.5-pro"],
        help="Flash is faster; Pro is smarter for complex logic."
    )
    
    if st.button("+ New Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    # FEATURE 2: VOICE INPUT TAB
    st.write("🎙️ Audio Link")
    audio_data = st.audio_input("Record to speak")

# --- 5. MAIN CHAT & STREAMING ---
st.markdown(f'<h1 class="nexus-header">Greetings, {st.session_state.user_name}</h1>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="✨" if message["role"] == "assistant" else None):
        st.markdown(message["content"])

# --- 6. INPUT HANDLING (Voice + Text) ---
user_query = st.chat_input("Ask anything...")

# If voice is recorded, use it as the prompt
if audio_data:
    # Note: In a real app, you'd send the audio_data to Gemini's multimodal endpoint
    # For now, we notify the user we are processing the audio
    user_query = "Please analyze my voice message." 

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # FEATURE 3: STREAMING RESPONSE
    with st.chat_message("assistant", avatar="✨"):
        try:
            ctx = st.session_state.memory_data.get('chat_summary', '')
            
            # Using generate_content_stream for that "typing" effect
            stream = client.models.generate_content_stream(
                model=model_choice,
                contents=f"User: {st.session_state.user_name}. Context: {ctx}. Task: {user_query}"
            )
            
            # Using st.write_stream to render chunks as they arrive
            def stream_data():
                for chunk in stream:
                    yield chunk.text

            full_response = st.write_stream(stream_data)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            if "429" in str(e):
                st.warning("⚡ Neural Cooldown Active. System resting...")
            else:
                st.error(f"Error: {e}")
