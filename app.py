import streamlit as st
import json
import base64
import requests
from io import BytesIO
from groq import Groq
from github import Github
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS

# --- 1. CORE ENGINE STABILITY CHECK ---
@st.cache_resource
def init_nexus():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return g_client, r
    except Exception as e:
        return None, None

client, repo = init_nexus()

# --- 2. THE VISUAL CLONE ENGINE (CSS) ---
st.set_page_config(page_title="Nexus Pro v3.2", layout="wide", initial_sidebar_state="collapsed")

if "theme_mode" not in st.session_state: st.session_state.theme_mode = "Dark"
bg, card, text = ("#0E1117", "#1A1C23", "#E0E0E0") if st.session_state.theme_mode == "Dark" else ("#F0F2F6", "#FFFFFF", "#1E1E1E")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; background-color: {bg} !important; color: {text} !important; }}
    
    /* Main Centered Card matching your Image */
    .main-wrapper {{
        background: {card}; border-radius: 24px; padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 20px 60px rgba(0,0,0,0.6);
        max-width: 1200px; margin: auto;
    }}
    
    .nexus-title {{
        font-size: 45px; font-weight: 700; margin-bottom: 25px;
        background: linear-gradient(135deg, #58a6ff 0%, #bc8cff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}

    /* Custom Button Tabs matching the image navigation */
    .stTabs [data-baseweb="tab-list"] {{ gap: 12px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255,255,255,0.05) !important; border-radius: 12px !important;
        padding: 12px 24px !important; border: 1px solid rgba(255,255,255,0.1) !important;
        color: #8b949e !important; height: 55px; transition: 0.3s;
    }}
    .stTabs [aria-selected="true"] {{
        border: 2px solid #58a6ff !important; background-color: rgba(88, 166, 255, 0.1) !important;
        color: white !important;
    }}
    
    /* Hide Streamlit elements */
    header, footer {{ visibility: hidden; }}
    .block-container {{ padding-top: 3rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. MASTER APPLICATION UI ---
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

head_l, head_r = st.columns([7, 3])
with head_l: st.markdown('<div class="nexus-title">Nexus Omni <span style="font-size:16px; color:#8b949e; font-weight:400;">v3.2 Pro</span></div>', unsafe_allow_html=True)
with head_r: st.session_state.theme_mode = st.radio("Appearance", ["Dark", "Light"], horizontal=True, label_visibility="collapsed")

# Tab definition - initialized before use to prevent NameError
tabs = st.tabs(["🖋️ Architect & Vault", "💬 English Chat", "🎙️ English Voice", "🖼️ Media Studio", "🧪 Live Sandbox"])

# TAB 1: ARCHITECT
with tabs[0]:
    st.subheader("Production Vault")
    arch_c1, arch_c2 = st.columns(2)
    with arch_c1:
        fname = st.text_input("Filename", "app.py", key="arch_filename")
        fcode = st.text_area("Source Code", height=250, key="arch_source")
        if st.button("🚀 Push to GitHub", use_container_width=True):
            if repo:
                try:
                    try: 
                        target = repo.get_contents(fname)
                        repo.update_file(fname, "Architect Sync", fcode, target.sha)
                    except: 
                        repo.create_file(fname, "Architect Init", fcode)
                    st.success("Deployment Successful!")
                except Exception as e: st.error(f"GitHub Error: {e}")
    with arch_c2:
        st.info("Scanning Repository...")
        if repo:
            try:
                for f in repo.get_contents(""):
                    if f.type == "file": st.text(f"📄 {f.name}")
            except: st.warning("Connection to GitHub repo failed.")

# TAB 2: CHAT
with tabs[1]:
    if "messages" not in st.session_state: st.session_state.messages = []
    chat_box = st.container(height=400, border=True)
    for m in st.session_state.messages:
        with chat_box.chat_message(m["role"]): st.markdown(m["content"])
    
    # Action buttons from visual image
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    p_cmd = None
    if c_btn1.button("🔍 Audit Code", use_container_width=True): p_cmd = "Audit the security of my code."
    if c_btn2.button("📐 UI UX", use_container_width=True): p_cmd = "Suggest 3 UI improvements."
    if c_btn3.button("🧠 Sync Memory", use_container_width=True): p_cmd = "Review our project status."

    query = st.chat_input("Command the Nexus in English...") or p_cmd
    if query and client:
        st.session_state.messages.append({"role": "user", "content": query})
        with chat_box.chat_message("user"): st.markdown(query)
        with chat_box.chat_message("assistant"):
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"Reply ONLY in English."}]+st.session_state.messages).choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

# TAB 3: VOICE
with tabs[2]:
    st.subheader("English Voice AI")
    audio = mic_recorder(start_prompt="🎤 Start Talking", stop_prompt="🛑 Stop Talking", key='v_bot')
    if audio and client:
        with st.spinner("Processing Voice..."):
            a_data = BytesIO(audio['bytes']); a_data.name = "audio.wav"
            text_trans = client.audio.transcriptions.create(model="whisper-large-v3", file=a_data).text
            ai_res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":text_trans}]).choices[0].message.content
            st.write(f"**Recognized:** {text_trans}")
            st.write(f"**Nexus:** {ai_res}")
            tts = gTTS(text=ai_res, lang='en'); b_io = BytesIO(); tts.write_to_fp(b_io)
            st.audio(b_io.getvalue(), format="audio/mp3", autoplay=True)

# TAB 4: MEDIA STUDIO (Fixed Image Logic)
with tabs[3]:
    st.subheader("Media Studio")
    m_prompt = st.text_input("Image Description:", key="media_input")
    if st.button("✨ Generate Professional Asset", use_container_width=True):
        if m_prompt:
            # High-fidelity pollinations link with no-cache to force refresh
            img_url = f"https://image.pollinations.ai/prompt/{m_prompt.replace(' ', '%20')}?width=1024&height=768&nologo=true&seed=42"
            st.image(img_url, caption=m_prompt, use_container_width=True)

# TAB 5: SANDBOX
with tabs[4]:
    st.subheader("Live Sandbox")
    test_code = st.text_area("Test Script:", value='st.balloons()\nst.success("System Fully Online!")', height=150)
    if st.button("⚙️ Execute Code"):
        try: exec(test_code)
        except Exception as e: st.error(f"Sandbox Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)
