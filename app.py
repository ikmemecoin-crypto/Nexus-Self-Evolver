import streamlit as st
import json
from groq import Groq
from github import Github

# --- 1. CORE INTEGRATION ---
@st.cache_resource
def connect_system():
    try:
        g = Groq(api_key=st.secrets["GROQ_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return g, r
    except: return None, None

client, repo = connect_system()

# --- 2. THE 99.9% GEMINI INTERFACE STYLING ---
st.set_page_config(page_title="Gemini", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    html, body, [class*="st-"] { font-family: 'Google Sans', sans-serif; background-color: #131314 !important; color: #E3E3E3 !important; }
    [data-testid="stSidebar"] { background-color: #1E1F20 !important; border-right: none; }
    .gemini-gradient {
        font-size: 44px; font-weight: 500;
        background: linear-gradient(74deg, #4285f4 0%, #9b72cb 20%, #d96570 40%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-top: 50px;
    }
    .stChatInputContainer { padding: 0px !important; background: transparent !important; }
    div[data-testid="stChatInput"] { background-color: #1E1F20 !important; border-radius: 32px !important; border: 1px solid #3C4043 !important; }
    [data-testid="stSidebar"] { display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (HIDDEN NEXUS ENGINE) ---
with st.sidebar:
    st.markdown("### 🛰️ Nexus Control")
    with st.expander("✍️ Auto-Writer"):
        fn = st.text_input("Filename", "main.py")
        src = st.text_area("Source Code", height=200)
        if st.button("🚀 Deploy"):
            try:
                try: 
                    old = repo.get_contents(fn)
                    repo.update_file(fn, "Gemini Sync", src, old.sha)
                except: repo.create_file(fn, "Gemini Init", src)
                st.toast("Production Sync Complete!")
            except Exception as e: st.error(e)

    with st.expander("📁 File Manager"):
        try:
            for f in repo.get_contents(""):
                if f.type == "file": st.caption(f"📄 {f.name}")
        except: pass

# --- 4. MAIN INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) == 0:
    st.markdown('<div class="gemini-gradient">Hello, Adil</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 44px; color: #444746; font-weight: 500;">How can I help you today?</div>', unsafe_allow_html=True)
else:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# --- 5. FIXED CHAT LOGIC ---
query = st.chat_input("Enter a prompt here")

if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    st.rerun()

# Safety Check for the Message History
if len(st.session_state.get("messages", [])) > 0:
    if st.session_state.messages[-1]["role"] == "user":
        user_text = st.session_state.messages[-1]["content"]
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile", 
                        messages=[{"role": "user", "content": user_text}]
                    )
                    ans = res.choices[0].message.content
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                    st.rerun()
                except Exception as e: st.error(e)
