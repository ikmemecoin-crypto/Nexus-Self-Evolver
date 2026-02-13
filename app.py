import streamlit as st
import json
import io
from PIL import Image

# --- 1. CORE ENGINE & SYNC ---
try:
    from groq import Groq
    from github import Github
except ImportError:
    st.error("Missing Libraries! Update requirements.txt")
    st.stop()

@st.cache_resource
def init_nexus():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return g_client, r
    except Exception as e:
        st.error(f"Nexus Sync Offline: {e}")
        return None, None

client, repo = init_nexus()

# --- 2. 100% NEW REDESIGN (GEMINI X GROK STYLE) ---
st.set_page_config(page_title="Nexus", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&family=Space+Grotesk:wght@300;500&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Google Sans', sans-serif; 
        background-color: #0b0b0b !important; 
        color: #f0f0f0 !important; 
    }

    /* Remove sidebar wall */
    [data-testid="stSidebar"] { background-color: #0b0b0b !important; border: none !important; }

    /* The Gemini x Grok Attraction Gradient */
    .hero-text {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.2rem; font-weight: 500;
        background: linear-gradient(120deg, #4285F4, #9B72CB, #D96570, #ffffff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem; text-align: center;
    }

    .main .block-container { max-width: 850px; padding-top: 4rem; margin: auto; }

    /* Floating Suggested Cards */
    .card-container { display: flex; gap: 10px; justify-content: center; margin-bottom: 2rem; flex-wrap: wrap; }
    .suggested-card {
        background: #1e1f20; border: 1px solid #333; border-radius: 12px;
        padding: 15px; width: 180px; font-size: 0.85rem; color: #ccc;
        cursor: pointer; transition: 0.3s;
    }
    .suggested-card:hover { background: #2a2b2d; border-color: #4285F4; }

    /* Pill Input Bar */
    .stChatInputContainer {
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 28px !important;
        padding: 10px 20px !important;
        position: fixed; bottom: 30px;
    }
    
    /* Message Styling */
    .stChatMessage { padding: 1rem 0 !important; border: none !important; }
    
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (AUTO-WRITER SETTINGS) ---
with st.sidebar:
    st.markdown("<h2 style='color:#4285F4;'>Nexus Vault</h2>", unsafe_allow_html=True)
    project = st.selectbox("Vault Focus", ["General", "Coding", "Research"], label_visibility="collapsed")
    st.markdown("---")
    with st.expander("🛠️ Architect Console"):
        fname = st.text_input("File Path", "nexus_app.py")
        code_to_push = st.text_area("Source Code", height=200)
        if st.button("🚀 Deploy to GitHub"):
            try:
                repo.create_file(fname, "Architect Deploy", code_to_push)
                st.success("File Pushed Successfully.")
            except Exception as e: st.error(e)

# --- 4. FRONT PAGE & SUGGESTED CARDS ---
st.markdown('<div class="hero-text">Hello, Adil</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:1.4rem; color:#888; margin-bottom:2rem;'>How can I help you architect today?</p>", unsafe_allow_html=True)

# Suggested Cards Logic
cols = st.columns(4)
suggestions = [
    "📝 Write a Python script for automation",
    "🧠 Brainstorm new features for Nexus",
    "🎨 Improve my app's UI/UX",
    "🚀 Deploy current code to GitHub"
]
for i, col in enumerate(cols):
    with col:
        st.markdown(f'<div class="suggested-card">{suggestions[i]}</div>', unsafe_allow_html=True)

# --- 5. CHAT SYSTEM ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Centered Chat History
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
        st.markdown(m["content"])

# FLOATING INPUT
query = st.chat_input("Ask Nexus anything...")

# --- 6. LOGIC & AUTO-LEARN ---
if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("assistant", avatar="✨"):
        try:
            # Atomic Memory Sync
            mem_path = f"memory_{project.lower()}.json"
            try:
                f_meta = repo.get_contents(mem_path)
                vault = json.loads(f_meta.decoded_content.decode())
                sha = f_meta.sha
            except:
                vault, sha = {"history": []}, None

            # Generate
            comp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": query}]
            )
            ans = comp.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

            # Learning Sync (Write back to GitHub)
            if "history" not in vault: vault["history"] = []
            vault["history"].append(query[:60])
            if sha: repo.update_file(mem_path, "Nexus Learning", json.dumps(vault), sha)
            else: repo.create_file(mem_path, "Nexus Init", json.dumps(vault))
            
            st.rerun()
        except Exception as e:
            st.error(f"Neural Error: {e}")
