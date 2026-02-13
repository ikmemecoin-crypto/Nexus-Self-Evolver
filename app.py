import streamlit as st
import json
import io
from PIL import Image

# --- 1. CORE ENGINE ---
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

# --- 2. 100% VISUAL REDESIGN (GEMINI X GROK COLORS) ---
st.set_page_config(page_title="Nexus", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    
    /* Grok-style Deep Black Background */
    html, body, [class*="st-"] { 
        font-family: 'Google Sans', sans-serif; 
        background-color: #080808 !important; 
        color: #f0f0f0 !important; 
    }

    /* Gemini-style Attraction Gradient for Header */
    .hero-text {
        font-size: 3.5rem; font-weight: 500;
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-top: 2rem;
    }

    /* Sidebar Styling (Base Standard Kept) */
    [data-testid="stSidebar"] { 
        background-color: #111111 !important; 
        border-right: 1px solid #222 !important; 
    }
    
    /* Pill Input Bar (Gemini Style) */
    .stChatInputContainer {
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 28px !important;
        padding: 5px 15px !important;
    }

    /* Suggested Cards */
    .suggested-card {
        background: #161616; border: 1px solid #222; border-radius: 12px;
        padding: 15px; font-size: 0.9rem; color: #aaa; text-align: center;
        transition: 0.3s; cursor: pointer;
    }
    .suggested-card:hover { border-color: #4285F4; background: #1c1c1c; }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (BASE STANDARD CONTROL PANEL) ---
with st.sidebar:
    st.markdown("<h2 style='color:#4285F4;'>Nexus Vault</h2>", unsafe_allow_html=True)
    project = st.selectbox("Vault Focus", ["General", "Coding", "Research"])
    st.markdown("---")
    st.markdown("### ✍️ Auto-Writer")
    fname = st.text_input("File Name", "logic.py")
    code_body = st.text_area("Code to Deploy", height=200)
    if st.button("🚀 Push to GitHub"):
        try:
            repo.create_file(fname, "Architect Deploy", code_body)
            st.success("File Pushed.")
        except Exception as e: st.error(e)

# --- 4. FRONT PAGE DISPLAY ---
st.markdown('<div class="hero-text">Nexus Omni</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666; font-size:1.2rem;'>Architecting the future with precision.</p>", unsafe_allow_html=True)

# Suggested Cards (Attraction Feature)
c1, c2, c3, c4 = st.columns(4)
prompts = ["📝 Code Script", "🧠 Brainstorm", "🎨 UI Design", "🚀 Deploy App"]
for i, col in enumerate([c1, c2, c3, c4]):
    col.markdown(f'<div class="suggested-card">{prompts[i]}</div>', unsafe_allow_html=True)

# --- 5. CHAT ENGINE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
        st.markdown(m["content"])

query = st.chat_input("How can I help you today, Adil?")

# --- 6. LOGIC ---
if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("assistant", avatar="✨"):
        try:
            # Sync Logic
            mem_path = f"memory_{project.lower()}.json"
            try:
                f = repo.get_contents(mem_path); vault = json.loads(f.decoded_content.decode()); sha = f.sha
            except:
                vault, sha = {"history": []}, None

            # Generate
            comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": query}])
            ans = comp.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

            # Save Learning
            vault["history"].append(query[:50])
            if sha: repo.update_file(mem_path, "Sync", json.dumps(vault), sha)
            else: repo.create_file(mem_path, "Init", json.dumps(vault))
            st.rerun()
        except Exception as e: st.error(e)
