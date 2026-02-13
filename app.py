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

# --- 2. BASE STANDARD LAYOUT + ATTRACTIVE STYLING ---
st.set_page_config(page_title="Nexus", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    html, body, [class*="st-"] { font-family: 'Google Sans', sans-serif; background-color: #080808 !important; color: #f0f0f0 !important; }

    /* Gemini-Grok Header */
    .hero-text {
        font-size: 3.5rem; font-weight: 500;
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-top: 1rem;
    }

    /* Sidebar Base Standard */
    [data-testid="stSidebar"] { background-color: #111111 !important; border-right: 1px solid #222 !important; }
    
    /* Pill Input Bar */
    .stChatInputContainer {
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 28px !important;
    }

    /* Suggested Cards */
    .stButton > button {
        background-color: #161616 !important;
        border: 1px solid #222 !important;
        color: #aaa !important;
        border-radius: 12px !important;
        padding: 20px !important;
        width: 100% !important;
        transition: 0.3s !important;
    }
    .stButton > button:hover { border-color: #4285F4 !important; color: white !important; background: #1c1c1c !important; }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (BASE STANDARD CONTROLS) ---
with st.sidebar:
    st.markdown("<h2 style='color:#4285F4;'>Nexus Vault</h2>", unsafe_allow_html=True)
    project = st.selectbox("Vault Focus", ["General", "Coding", "Research"])
    st.markdown("---")
    st.markdown("### ✍️ Auto-Writer")
    fname = st.text_input("File Name", "logic.py")
    code_body = st.text_area("Code to Deploy", height=150)
    if st.button("🚀 Push to GitHub"):
        try:
            repo.create_file(fname, "Architect Deploy", code_body)
            st.success("Deployed to GitHub!")
        except Exception as e: st.error(f"Write Error: {e}")

# --- 4. FRONT PAGE DISPLAY ---
st.markdown('<div class="hero-text">Nexus Omni</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666; font-size:1.2rem; margin-bottom:20px;'>Architecting the future with precision.</p>", unsafe_allow_html=True)

# Functional Suggested Cards
c1, c2, c3, c4 = st.columns(4)
suggested_query = None

with c1: 
    if st.button("📝 Code Script"): suggested_query = "Write a Python script for automation"
with c2: 
    if st.button("🧠 Brainstorm"): suggested_query = "Brainstorm new features for this app"
with c3: 
    if st.button("🎨 UI Design"): suggested_query = "How can I make this UI even more attractive?"
with c4: 
    if st.button("🚀 Deploy App"): suggested_query = "Show me how to deploy this app to a custom domain"

# --- 5. CHAT ENGINE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
        st.markdown(m["content"])

user_input = st.chat_input("How can I help you today, Adil?")
query = user_input or suggested_query

# --- 6. LOGIC & AUTO-LEARNING ---
if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("assistant", avatar="✨"):
        try:
            # Sync Logic (Atomic Fetch to prevent 409 Conflict)
            mem_path = f"memory_{project.lower()}.json"
            try:
                f = repo.get_contents(mem_path)
                vault = json.loads(f.decoded_content.decode())
                sha = f.sha
            except:
                vault, sha = {"history": []}, None

            # Generate response
            comp = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "user", "content": query}]
            )
            ans = comp.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

            # Save to Learning Vault
            if "history" not in vault: vault["history"] = []
            vault["history"].append(query[:60])
            if sha: repo.update_file(mem_path, "Learning Sync", json.dumps(vault), sha)
            else: repo.create_file(mem_path, "Vault Init", json.dumps(vault))
            
            st.rerun()
        except Exception as e:
            st.error(f"System Error: {e}")
