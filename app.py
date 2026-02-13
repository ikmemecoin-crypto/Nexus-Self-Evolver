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

# --- 2. 99.9% PIXEL PERFECT CSS ---
st.set_page_config(page_title="Gemini", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap');
    html, body, [class*="st-"] { font-family: 'Google Sans', sans-serif; background-color: #131314 !important; color: #E3E3E3 !important; }
    header, footer { visibility: hidden; }
    
    /* Pill Styling */
    .stButton > button {
        background-color: #1E1F20 !important;
        color: #E3E3E3 !important;
        border: 1px solid #3C4043 !important;
        border-radius: 20px !important;
        padding: 10px 20px !important;
        transition: 0.3s;
    }
    .stButton > button:hover { border-color: #8E918F !important; background-color: #28292A !important; }

    /* Input Area */
    div[data-testid="stChatInput"] { background-color: #1E1F20 !important; border-radius: 28px !important; border: 1px solid #3C4043 !important; }
    
    .gemini-gradient {
        font-size: 56px; font-weight: 500;
        background: linear-gradient(74deg, #4285f4 0%, #9b72cb 15%, #d96570 35%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-top: 5vh;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE INTERFACE ---
if "messages" not in st.session_state: st.session_state.messages = []

# Top Model Selector (Gemini 3 Style)
col_sel, col_space = st.columns([2, 8])
with col_sel:
    model_version = st.selectbox("Model", ["Gemini 3.0 Pro", "Gemini 1.5 Flash", "Nexus Ultra"], label_visibility="collapsed")

# Main Screen
p_input = None
if not st.session_state.messages:
    st.markdown('<div class="gemini-gradient">Hi Adil</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 56px; color: #444746; font-weight: 500; margin-bottom: 40px;">Where should we start?</div>', unsafe_allow_html=True)
    
    # Active Suggestion Pills
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🎨 Create image"): p_input = "Generate a professional logo for a new AI startup."
    if c2.button("💡 Help me learn"): p_input = "Explain how to scale a SaaS business to $2,000/month."
    if c3.button("📝 Write anything"): p_input = "Write a cold email to a real estate client for my ROI tool."
    if c4.button("🚀 Boost my day"): p_input = "Give me a high-productivity schedule to hit my monthly goals."

# Display Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- 4. HIDDEN ENGINE (SIDEBAR) ---
with st.sidebar:
    st.title("🛰️ Nexus Engine")
    st.success("Target: $2,000 / Current: $0")
    with st.expander("🛠️ GitHub Auto-Writer"):
        fn = st.text_input("Filename", "earning_logic.py")
        code = st.text_area("Source Code", height=200)
        if st.button("🚀 Deploy"):
            try:
                try:
                    f = repo.get_contents(fn); repo.update_file(fn, "Update", code, f.sha)
                except: repo.create_file(fn, "Init", code)
                st.toast("Deployed to Cloud!")
            except Exception as e: st.error(e)

# --- 5. CHAT LOGIC ---
query = st.chat_input("Ask Gemini 3") or p_input

if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"): st.markdown(query)
    
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            try:
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": query}])
                ans = res.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.rerun()
            except Exception as e: st.error(e)
