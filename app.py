import streamlit as st
from google import genai
import json
from github import Github
from PIL import Image
import io

# --- 1. CORE ENGINE STABILIZATION ---
st.set_page_config(page_title="Nexus Omni", layout="wide", initial_sidebar_state="expanded")

# Ultra-Clean Material Design (No "Walls", Single Page Fit)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Google Sans', sans-serif; 
        background-color: #131314; 
        color: #e3e3e3; 
    }

    /* Remove vertical scrolling by tightening containers */
    .block-container { padding: 1rem 3rem !important; }
    
    .google-header {
        font-size: 2.5rem;
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
        font-size: 0.9rem;
        margin-bottom: 10px;
    }

    /* Seamless Sidebar */
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border: none; }
    
    /* Search Bar Design */
    .stChatInputContainer { 
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 24px !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
@st.cache_resource
def setup_nexus():
    try:
        c = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return c, r
    except Exception as e:
        st.error(f"Nexus Core Offline: {e}")
        return None, None

client, repo = setup_nexus()

# --- 3. THE CONTROL PANEL (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Nexus</h2>", unsafe_allow_html=True)
    
    mode = st.selectbox("Engine Mode", ["Chat", "Web Search", "Python Lab"])
    project = st.selectbox("Vault", ["General", "Coding", "Personal", "Research"])
    
    # Memory Loader
    mem_file = f"memory_{project.lower()}.json"
    if 'vault_data' not in st.session_state or st.session_state.get('active_project') != project:
        try:
            raw = repo.get_contents(mem_file)
            st.session_state.vault_data = json.loads(raw.decoded_content.decode())
        except:
            st.session_state.vault_data = {"user": "Adil", "summary": ""}
        st.session_state.active_project = project

    st.markdown("---")
    img_in = st.file_uploader("Upload Visuals", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    aud_in = st.audio_input("Voice Command")

# --- 4. THE INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">Welcome, Adil. Project: {project}</div>', unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Main Column for Chat
c1, c2, c3 = st.columns([0.5, 5, 0.5])
with c2:
    # Set a fixed height for chat to force everything onto 1 page
    chat_box = st.container(height=450, border=False)
    
    with chat_box:
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
                st.markdown(m["content"])

    # Input System
    query = st.chat_input("Ask anything...")

    if query or img_in or aud_in:
        # User side
        user_text = query if query else "Processing Multimedia..."
        st.session_state.chat_history.append({"role": "user", "content": user_text})
        
        with st.chat_message("assistant", avatar="✨"):
            try:
                # Payload Preparation
                payload = [f"Context: {st.session_state.vault_data.get('summary', '')[:300]}"]
                if img_in: payload.append(Image.open(img_in))
                if aud_in: payload.append({"inline_data": {"data": aud_in.read(), "mime_type": "audio/wav"}})
                if query: payload.append(query)
                
                tool_config = [{"google_search": {}}] if mode == "Web Search" else None
                
                def generate():
                    for chunk in client.models.generate_content_stream(
                        model="gemini-2.0-flash", 
                        contents=payload, 
                        config={'tools': tool_config}
                    ):
                        if chunk.text: yield chunk.text

                full_reply = st.write_stream(generate())
                st.session_state.chat_history.append({"role": "assistant", "content": full_reply})
                st.rerun()
                
            except Exception as e:
                st.error(f"Neural Error: {e}")
