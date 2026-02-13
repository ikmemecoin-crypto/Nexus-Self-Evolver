import streamlit as st
import json
from groq import Groq
from github import Github

# --- 1. CORE SYNC ---
@st.cache_resource
def init_nexus():
    try:
        g = Groq(api_key=st.secrets["GROQ_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return g, r
    except: return None, None

client, repo = init_nexus()

# --- 2. EXACT GEMINI COLOR PALETTE & UI ---
st.set_page_config(page_title="Gemini", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    
    /* Background & Main Font */
    html, body, [class*="st-"] {
        font-family: 'Google Sans', sans-serif;
        background-color: #131314 !important;
        color: #E3E3E3 !important;
    }

    /* Remove Streamlit Header/Footer */
    header, footer { visibility: hidden; }
    
    /* The Chat Bubble Styling */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        margin-bottom: 1rem;
    }
    
    /* Input Container Fix at Bottom */
    .stChatInputContainer {
        padding-bottom: 20px !important;
        background-color: #131314 !important;
    }

    div[data-testid="stChatInput"] {
        background-color: #1E1F20 !important;
        border: 1px solid #3C4043 !important;
        border-radius: 28px !important;
    }

    /* The Gradient Welcome Text */
    .welcome-text {
        font-size: 56px;
        font-weight: 500;
        background: linear-gradient(74deg, #4285f4 0%, #9b72cb 15%, #d96570 35%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 10vh;
    }

    /* Sidebar/Settings Style */
    [data-testid="stSidebar"] {
        background-color: #1E1F20 !important;
        border-right: 1px solid #3C4043;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main Layout
if not st.session_state.messages:
    st.markdown('<div class="welcome-text">Hi Adil</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 56px; color: #444746; font-weight: 500; margin-bottom: 40px;">Where should we start?</div>', unsafe_allow_html=True)
    
    # Suggestion Pills (Pill-style like your image)
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🎨 Create image", use_container_width=True): pass
    if c2.button("💡 Help me learn", use_container_width=True): pass
    if c3.button("📝 Write anything", use_container_width=True): pass
    if c4.button("🚀 Boost my day", use_container_width=True): pass

# Display Chat History
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 4. THE HIDDEN ENGINE (SIDEBAR) ---
with st.sidebar:
    st.title("🛰️ Nexus Settings")
    with st.expander("🛠️ Developer Tools"):
        fn = st.text_input("Deploy Filename", "app_v2.py")
        code = st.text_area("Live Code Editor", height=300)
        if st.button("🚀 Push to GitHub"):
            try:
                try:
                    f = repo.get_contents(fn)
                    repo.update_file(fn, "Sync", code, f.sha)
                except:
                    repo.create_file(fn, "Init", code)
                st.toast("Production updated!")
            except Exception as e: st.error(e)

# --- 5. CHAT LOGIC ---
prompt = st.chat_input("Ask Gemini 3")

if prompt and client:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if len(st.session_state.get("messages", [])) > 0:
    if st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": st.session_state.messages[-1]["content"]}]
                )
                response = stream.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                st.error(f"Nexus Sync Error: {e}")
