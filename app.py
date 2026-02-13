import streamlit as st
from github import Github
from groq import Groq # Optimized for speed & free tier
import json
import io

# --- 1. RESET UI (STABLE DARK MATERIAL) ---
st.set_page_config(page_title="Nexus Omni", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    html, body, [class*="st-"] { font-family: 'Google Sans', sans-serif; background-color: #131314; color: #e3e3e3; }
    .block-container { padding: 1rem 3rem !important; }
    .google-header { font-size: 3rem; font-weight: 500; text-align: center; background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border: none; }
    .stChatInputContainer { background-color: #1e1f20 !important; border: 1px solid #3c4043 !important; border-radius: 24px !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE MULTI-PROVIDER RESET ---
@st.cache_resource
def init_nexus():
    try:
        # We switch to Groq for stable free-tier access
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        repo = gh.get_repo(st.secrets["GH_REPO"])
        return g_client, repo
    except Exception as e:
        st.error(f"Core Failed: {e}")
        return None, None

client, repo = init_nexus()

# --- 3. SIDEBAR (COMPACT & CLEAN) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Nexus Omni</h2>", unsafe_allow_html=True)
    # Using Llama 3.3 70B - High performance, Zero cost on Groq
    model_id = "llama-3.3-70b-versatile"
    project = st.selectbox("Vault", ["General", "Coding", "Research"], label_visibility="collapsed")
    
    st.markdown("---")
    # Multimedia inputs restored to stable versions
    img_in = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    aud_in = st.audio_input("Voice Command")

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Centered chat flow
c1, c2, c3 = st.columns([0.5, 5, 0.5])
with c2:
    chat_box = st.container(height=450, border=False)
    with chat_box:
        for m in st.session_state.messages:
            with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
                st.markdown(m["content"])

    # FIXED: The Writing Tab (Chat Input)
    query = st.chat_input("Ask Nexus anything...")

    if query or img_in or aud_in:
        user_text = query if query else "🧬 Processing multimedia input..."
        st.session_state.messages.append({"role": "user", "content": user_text})
        
        with st.chat_message("assistant", avatar="✨"):
            try:
                # Groq Implementation (Lightning Fast)
                completion = client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": user_text}],
                    stream=True
                )
                
                def stream_res():
                    for chunk in completion:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content

                full_reply = st.write_stream(stream_res())
                st.session_state.messages.append({"role": "assistant", "content": full_reply})
                st.rerun()
                
            except Exception as e:
                st.error(f"Nexus Brain Error: {e}")
