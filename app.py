import streamlit as st
import json
import io
from PIL import Image

# --- 1. CORE IMPORTS & ERROR HANDLING ---
try:
    from groq import Groq
    from github import Github
except ImportError:
    st.error("Check requirements.txt: groq and PyGithub are required.")
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

# --- 3. FRONT PAGE LAYOUT (MINIMALIST MATERIAL) ---
st.set_page_config(page_title="Nexus Omni", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    html, body, [class*="st-"] { font-family: 'Google Sans', sans-serif; background-color: #131314; color: #e3e3e3; }
    
    .google-header { 
        font-size: 3.5rem; font-weight: 500; text-align: center; 
        background: linear-gradient(90deg, #4285F4 0%, #34A853 30%, #FBBC05 60%, #EA4335 100%); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        padding-top: 20px;
    }
    
    /* Center the chat container */
    .chat-wrapper { max-width: 800px; margin: auto; }
    
    /* Bottom Control Panel Styling */
    .bottom-panel {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #1e1f20; border-top: 1px solid #3c4043;
        padding: 10px 20px; z-index: 99;
    }

    [data-testid="stSidebar"] { display: none; } /* Moving features from sidebar to bottom */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FRONT PAGE HEADER ---
st.markdown('<div class="google-header">Nexus Omni</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#8e918f;'>System: Optimal | Architect Mode Active</p>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. CHAT DISPLAY ---
chat_area = st.container(height=450, border=False)
with chat_area:
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else None):
            st.markdown(m["content"])

# --- 6. BOTTOM CONTROL PANEL & INPUT ---
st.markdown('<div class="bottom-panel">', unsafe_allow_html=True)
cols = st.columns([2, 2, 6])

with cols[0]:
    project = st.selectbox("Vault", ["General", "Coding", "Research"], label_visibility="collapsed")

with cols[1]:
    # Quick Upload for media
    uploaded_file = st.file_uploader("Upload", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

with cols[2]:
    query = st.chat_input("Command Nexus...")

# Auto-Writer (Bottom Expanded Feature)
with st.expander("✍️ Auto-Writer & Deployment Console"):
    cw1, cw2 = st.columns([1, 2])
    fname = cw1.text_input("Filename", "nexus_module.py")
    code_in = cw2.text_area("Source Code", height=100)
    if st.button("🚀 Deploy to GitHub"):
        try:
            repo.create_file(fname, f"Nexus Auto-Deploy", code_in)
            st.success("Deployed!")
        except Exception as e: st.error(f"Error: {e}")

# --- 7. EXECUTION LOGIC ---
if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with chat_area:
        with st.chat_message("assistant", avatar="✨"):
            try:
                # Fresh SHA fetch for Learning Sync (Prevents 409 error)
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

                # Sync Learning
                vault["history"].append(query[:50])
                if sha: repo.update_file(mem_path, "Sync", json.dumps(vault), sha)
                else: repo.create_file(mem_path, "Init", json.dumps(vault))
                
                st.rerun()
            except Exception as e: st.error(f"Neural Error: {e}")
