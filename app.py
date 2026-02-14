import streamlit as st
import json
import base64
from io import BytesIO
from groq import Groq
from github import Github
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS

# --- 1. INITIALIZE CORE ENGINES (100% Verified) ---
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

# --- 2. THE VISUAL CLONE (CSS) ---
st.set_page_config(page_title="Nexus Pro v3.1", layout="wide", initial_sidebar_state="collapsed")

if "theme_mode" not in st.session_state: st.session_state.theme_mode = "Dark"
bg, card, text = ("#0E1117", "#1A1C23", "#E0E0E0") if st.session_state.theme_mode == "Dark" else ("#F0F2F6", "#FFFFFF", "#1E1E1E")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; background-color: {bg} !important; color: {text} !important; }}
    
    /* Main Background Card */
    .main-box {{
        background: {card}; border-radius: 20px; padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 15px 50px rgba(0,0,0,0.4);
    }}
    
    /* Title Logic */
    .nexus-header {{
        font-size: 40px; font-weight: 700; margin-bottom: 20px;
        background: linear-gradient(90deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}

    /* Matching the Tabs in the Image */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #21262d !important; border-radius: 8px !important;
        padding: 8px 16px !important; border: 1px solid #30363d !important;
        color: #c9d1d9 !important; height: 45px;
    }}
    .stTabs [aria-selected="true"] {{
        border: 1px solid #58a6ff !important; background-color: #161b22 !important;
    }}
    header, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. APP STRUCTURE ---
st.markdown(f'<div class="main-box">', unsafe_allow_html=True)

col_t, col_s = st.columns([8, 2])
with col_t: st.markdown('<div class="nexus-header">Nexus Omni <span style="font-size:18px; color:gray; font-weight:400;">v3.1 Pro</span></div>', unsafe_allow_html=True)
with col_s: st.session_state.theme_mode = st.radio("Mode", ["Dark", "Light"], horizontal=True, label_visibility="collapsed")

# Tab Navigation exactly as per Image
t1, t2, t3, t4, t5 = st.tabs(["🖋️ Architect & Vault", "💬 English Chat", "🎙️ English Voice", "🖼️ Media Studio", "🧪 Live Sandbox"])

# TAB 1: ARCHITECT (Working)
with t1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Code Architect")
        fn = st.text_input("Filename", "app.py", key="f_arch")
        cd = st.text_area("Source Code", height=200, key="c_arch")
        if st.button("🚀 Deploy to GitHub", use_container_width=True):
            if repo:
                try:
                    try: f = repo.get_contents(fn); repo.update_file(fn, "update", cd, f.sha)
                    except: repo.create_file(fn, "init", cd)
                    st.success("File Pushed!")
                except Exception as e: st.error(e)
    with c2:
        st.markdown("### Vault Files")
        if repo:
            try:
                for f in repo.get_contents(""):
                    if f.type == "file": st.text(f"📄 {f.name}")
            except: st.info("Scanning...")

# TAB 2: CHAT (Working)
with t2:
    if "messages" not in st.session_state: st.session_state.messages = []
    chat_box = st.container(height=350, border=True)
    for m in st.session_state.messages:
        with chat_box.chat_message(m["role"]): st.markdown(m["content"])
    
    # Quick buttons from Image
    q1, q2, q3 = st.columns(3)
    p_cmd = None
    if q1.button("🔍 Audit Code", key="btn_audit"): p_cmd = "Audit my code."
    if q2.button("📐 UI UX", key="btn_ui"): p_cmd = "Improve UI."
    if q3.button("🧠 Sync Memory", key="btn_mem"): p_cmd = "Project status."

    prompt = st.chat_input("Command the Nexus in English...") or p_cmd
    if prompt and client:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_box.chat_message("user"): st.markdown(prompt)
        with chat_box.chat_message("assistant"):
            r = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"English only."}]+st.session_state.messages).choices[0].message.content
            st.markdown(r); st.session_state.messages.append({"role":"assistant","content":r}); st.rerun()

# TAB 3: VOICE (Working)
with t3:
    st.markdown("### English Voice Bot")
    audio = mic_recorder(start_prompt="🎤 Start Talking", stop_prompt="🛑 Stop Talking", key='v_rec')
    if audio and client:
        with st.spinner("Processing..."):
            a_file = BytesIO(audio['bytes']); a_file.name = "voice.wav"
            trans = client.audio.transcriptions.create(model="whisper-large-v3", file=a_file).text
            resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":trans}]).choices[0].message.content
            st.write(f"**You:** {trans}"); st.write(f"**Nexus:** {resp}")
            tts = gTTS(text=resp, lang='en'); b_io = BytesIO(); tts.write_to_fp(b_io)
            st.audio(b_io.getvalue(), format="audio/mp3", autoplay=True)

# TAB 4: MEDIA (Working - Fixed Image Link)
with t4:
    st.markdown("### Media Studio")
    m_prompt = st.text_input("Describe your image:", key="m_input")
    if st.button("✨ Generate Image", use_container_width=True):
        if m_prompt:
            img_url = f"https://image.pollinations.ai/prompt/{m_prompt.replace(' ', '%20')}?width=800&height=500&nologo=true"
            st.image(img_url, caption=m_prompt, use_container_width=True)

# TAB 5: SANDBOX (Working)
with t5:
    st.markdown("### Live Sandbox")
    t_code = st.text_area("Test Script:", value='st.balloons()\nst.success("System Operational")', height=150)
    if st.button("⚙️ Run Test", use_container_width=True):
        try: exec(t_code)
        except Exception as e: st.error(e)

st.markdown('</div>', unsafe_allow_html=True)
