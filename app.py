import streamlit as st
import json
import io
from PIL import Image

# --- 1. CORE IMPORTS & VERIFICATION ---
try:
    from groq import Groq
    from github import Github
except ImportError:
    st.error("Missing Libraries! Run: pip install groq PyGithub")
    st.stop()

# --- 2. AUTHENTICATION ---
@st.cache_resource
def init_nexus():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return g_client, r
    except Exception as e:
        st.error(f"Sync Offline: {e}")
        return None, None

client, repo = init_nexus()

# --- 3. GEMINI STYLE CSS (100% ACCURACY CHECK) ---
st.set_page_config(page_title="Nexus", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    
    /* Overall Background */
    html, body, [class*="st-"] { 
        font-family: 'Google Sans', sans-serif; 
        background-color: #131314 !important; 
        color: #e3e3e3 !important; 
    }

    /* Main Container Padding */
    .main .block-container { max-width: 900px; padding-top: 5rem; }

    /* Gemini Header */
    .gemini-header {
        font-size: 2.2rem; font-weight: 500; margin-bottom: 2rem;
        background: linear-gradient(75deg, #4285F4, #D96570, #9B72CB);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    /* Chat Bubbles Style */
    .stChatMessage { background-color: transparent !important; border: none !important; }
    
    /* Floating Pill Input Bar */
    .stChatInputContainer {
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 32px !important;
        padding: 5px 15px !important;
        margin-bottom: 20px !important;
    }

    /* Sidebar minimalization */
    [data-testid="stSidebar"] { background-color: #131314 !important; border: none !important; }
    
    /* Hide default streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (HIDDEN SETTINGS) ---
with st.sidebar:
    st.markdown("### Settings")
    project = st.selectbox("Active Vault", ["General", "Coding", "Research"])
    st.markdown("---")
    # Deploy Feature (Moved to sidebar for cleaner chat)
    with st.expander("🚀 Deploy Code"):
        fname = st.text_input("Filename", "nexus_script.py")
        code_in = st.text_area("Code", height=150)
        if st.button("Push to GitHub"):
            try:
                repo.create_file(fname, "Auto-Deploy", code_in)
                st.success("File Pushed!")
            except Exception as e: st.error(e)

# --- 5. CHAT INTERFACE ---
st.markdown('<div class="gemini-header">Nexus Omni</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages (Wide Format)
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
        st.markdown(m["content"])

# Pill-shaped Input Bar
query = st.chat_input("Enter a prompt here")

# --- 6. LOGIC & AUTO-LEARN ---
if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("assistant", avatar="✨"):
        try:
            # Atomic Learning Sync (Fixes 409)
            mem_path = f"memory_{project.lower()}.json"
            try:
                f_meta = repo.get_contents(mem_path)
                vault = json.loads(f_meta.decoded_content.decode())
                sha = f_meta.sha
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

            # Save Learning
            if "history" not in vault: vault["history"] = []
            vault["history"].append(query[:50])
            if sha: repo.update_file(mem_path, "Nexus Sync", json.dumps(vault), sha)
            else: repo.create_file(mem_path, "Nexus Init", json.dumps(vault))
            
            st.rerun()
        except Exception as e:
            st.error(f"Neural Error: {e}")
