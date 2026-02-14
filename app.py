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

# --- 2. THE IMAGE-PERFECT UI ENGINE ---
st.set_page_config(page_title="Nexus Pro v2.9", layout="wide", initial_sidebar_state="collapsed")

if "theme_mode" not in st.session_state: st.session_state.theme_mode = "Dark"
bg, card, text, accent = ("#0E1117", "#1A1C23", "#E0E0E0", "#58a6ff") if st.session_state.theme_mode == "Dark" else ("#F0F2F6", "#FFFFFF", "#1E1E1E", "#007BFF")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; background-color: {bg} !important; color: {text} !important; }}
    
    /* Perfect Card Styling from your Image */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: {card}; border-radius: 20px; padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }}
    
    .main-title {{
        font-size: 42px; font-weight: 700; background: linear-gradient(90deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }}
    
    /* Tab Styling to match visual buttons */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 10px 20px; border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    [data-testid="stSidebar"] {{ display: none; }}
    header, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
c_h1, c_h2 = st.columns([8, 2])
with c_h1: st.markdown('<div class="main-title">Nexus Omni <span style="font-size:16px; color:gray; font-weight:400;">v2.9 Pro</span></div>', unsafe_allow_html=True)
with c_h2: st.session_state.theme_mode = st.radio("Appearance", ["Dark", "Light"], horizontal=True, label_visibility="collapsed")

# --- 4. NAVIGATION ---
t_arch, t_chat, t_voice, t_media, t_test = st.tabs([
    "🖋️ Architect & Vault", "💬 English Chat", "🎙️ English Voice", "🖼️ Media Studio", "🧪 Live Sandbox"
])

# --- TAB: ARCHITECT ---
with t_arch:
    st.subheader("Production Architect")
    fn = st.text_input("Filename", "logic.py")
    code = st.text_area("Code Input", height=250)
    if st.button("🚀 Push to Vault", use_container_width=True):
        try:
            try: f = repo.get_contents(fn); repo.update_file(fn, "Sync", code, f.sha)
            except: repo.create_file(fn, "Init", code)
            st.toast("Deployed Successfully!")
        except Exception as e: st.error(e)

# --- TAB: CHAT (The Core Feature) ---
with t_chat:
    if "messages" not in st.session_state: st.session_state.messages = []
    c_box = st.container(height=450, border=True)
    for m in st.session_state.messages:
        with c_box.chat_message(m["role"]): st.markdown(m["content"])
    
    # Quick Action Buttons from your Image
    q1, q2, q3 = st.columns(3)
    p_cmd = None
    if q1.button("🔍 Audit Code", use_container_width=True): p_cmd = "Review my code for optimizations."
    if q2.button("📐 UI UX", use_container_width=True): p_cmd = "How can I improve the layout further?"
    if q3.button("🧠 Sync Memory", use_container_width=True): p_cmd = "Summarize our project status."

    prompt = st.chat_input("Command the Nexus...") or p_cmd
    if prompt and client:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with c_box.chat_message("user"): st.markdown(prompt)
        with c_box.chat_message("assistant"):
            ans = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are Nexus. Respond ONLY in English."}] + st.session_state.messages
            ).choices[0].message.content
            st.markdown(ans); st.session_state.messages.append({"role": "assistant", "content": ans}); st.rerun()

# --- TAB: VOICE ---
with t_voice:
    st.subheader("English Voice Interface")
    audio = mic_recorder(start_prompt="🎤 Start", stop_prompt="🛑 Stop", key='voice_mic')
    if audio and client:
        with st.spinner("Processing Voice..."):
            audio_bio = BytesIO(audio['bytes']); audio_bio.name = "audio.wav"
            trans = client.audio.transcriptions.create(model="whisper-large-v3", file=audio_bio).text
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", 
                  messages=[{"role": "system", "content": "Reply in English."}, {"role": "user", "content": trans}]).choices[0].message.content
            st.write(f"**Recognized:** {trans}"); st.write(f"**Nexus:** {res}")
            tts = gTTS(text=res, lang='en'); b_io = BytesIO(); tts.write_to_fp(b_io)
            st.audio(b_io.getvalue(), format="audio/mp3", autoplay=True)

# --- TAB: MEDIA ---
with t_media:
    st.subheader("Media Generation")
    m_p = st.text_input("Image Description")
    if st.button("Generate"):
        url = f"https://image.pollinations.ai/prompt/{m_p.replace(' ', '%20')}"
        st.image(url, use_container_width=True)

# --- TAB: SANDBOX ---
with t_test:
    st.subheader("Live Testing Lab")
    test_c = st.text_area("Python Script", value='st.balloons()')
    if st.button("Execute"):
        try: exec(test_c)
        except Exception as e: st.error(e)
