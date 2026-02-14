import streamlit as st
import json
import base64
from io import BytesIO
from groq import Groq
from github import Github
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS

# --- 1. CORE SYNC ---
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

# --- 2. ADVANCED CSS FOR VISUAL MATCH ---
st.set_page_config(page_title="Nexus Pro v3.0", layout="wide", initial_sidebar_state="collapsed")

if "theme_mode" not in st.session_state: st.session_state.theme_mode = "Dark"
bg, card, text = ("#0E1117", "#1A1C23", "#E0E0E0") if st.session_state.theme_mode == "Dark" else ("#F0F2F6", "#FFFFFF", "#1E1E1E")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Main Background and Font */
    html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; background-color: {bg} !important; color: {text} !important; }}
    
    /* Central Concept Card */
    .main-container {{
        background: {card};
        border-radius: 24px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        margin: 10px auto;
    }}

    /* Title Styling */
    .nexus-title {{
        font-size: 48px; font-weight: 700; 
        background: linear-gradient(90deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}

    /* Custom Tab Buttons */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 15px; background-color: transparent !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px; border-radius: 12px !important;
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important; font-weight: 600 !important;
    }}
    .stTabs [aria-selected="true"] {{
        border: 2px solid #58a6ff !important;
        background-color: rgba(88, 166, 255, 0.1) !important;
    }}

    /* Remove standard Streamlit padding */
    .block-container {{ padding-top: 2rem; }}
    header, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE "INTERFACE CARD" WRAPPER ---
st.markdown(f'''
    <div class="main-container">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
            <div class="nexus-title">Nexus Omni <span style="font-size:18px; color:gray; font-weight:400;">v3.0 Pro</span></div>
        </div>
''', unsafe_allow_html=True)

# --- 4. NAVIGATION & CONTENT ---
tabs = st.tabs(["🖋️ Architect & Vault", "💬 English Chat", "🎙️ English Voice", "🖼️ Media Studio", "🧪 Live Sandbox"])

# ARCHITECT TAB
with tabs[0]:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Code Architect")
        fn = st.text_input("Filename", "logic.py", key="arch_fn")
        code = st.text_area("Code Input", height=200, key="arch_code")
        if st.button("🚀 Push to Vault"):
            st.toast("Syncing with GitHub...")
    with col2:
        st.markdown("### Repository Vault")
        st.info("Scanning for secure files...")

# CHAT TAB (Visually Matching the Center of your Image)
with tabs[1]:
    st.markdown("### English Intelligence")
    if "messages" not in st.session_state: st.session_state.messages = []
    c_box = st.container(height=400, border=True)
    for m in st.session_state.messages:
        with c_box.chat_message(m["role"]): st.markdown(m["content"])
    
    # Matching the Bottom Action Buttons
    b1, b2, b3 = st.columns(3)
    p_cmd = None
    if b1.button("🔍 Audit Code", use_container_width=True): p_cmd = "Review my code."
    if b2.button("📐 UI UX", use_container_width=True): p_cmd = "Improve layout."
    if b3.button("🧠 Sync Memory", use_container_width=True): p_cmd = "Status report."
    
    prompt = st.chat_input("Command the Nexus...") or p_cmd
    if prompt and client:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with c_box.chat_message("user"): st.markdown(prompt)
        with c_box.chat_message("assistant"):
            ans = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": "English only."}] + st.session_state.messages).choices[0].message.content
            st.markdown(ans); st.session_state.messages.append({"role": "assistant", "content": ans}); st.rerun()

# MEDIA STUDIO TAB (Fixed from your screenshot)
with tabs[3]:
    st.markdown("### Media Generation")
    m_p = st.text_input("Image Description", placeholder="e.g. US Flag")
    if st.button("✨ Generate Asset"):
        if m_p:
            url = f"https://image.pollinations.ai/prompt/{m_p.replace(' ', '%20')}?width=1024&height=1024&nologo=true"
            st.image(url, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True) # Closing Main Card

# Theme Switcher at bottom
st.session_state.theme_mode = st.radio("Appearance", ["Dark", "Light"], horizontal=True)
