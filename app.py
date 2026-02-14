import streamlit as st
import json
import io
from groq import Groq
from github import Github
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import base64

# --- 1. CORE SYNC & SECRETS ---
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

# --- 2. PROFESSIONAL UI/UX ENGINE ---
st.set_page_config(page_title="Nexus Pro v2.4", layout="wide", initial_sidebar_state="collapsed")

if "theme_mode" not in st.session_state: st.session_state.theme_mode = "Dark"
bg, card, text, accent = ("#0E1117", "#1A1C23", "#E0E0E0", "#58a6ff") if st.session_state.theme_mode == "Dark" else ("#F0F2F6", "#FFFFFF", "#1E1E1E", "#007BFF")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; background-color: {bg} !important; color: {text} !important; }}
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: {card}; border-radius: 16px; padding: 24px;
        border: 1px solid rgba(128, 128, 128, 0.2); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
    }}
    .main-title {{
        font-size: 36px; font-weight: 600; background: linear-gradient(120deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    [data-testid="stSidebar"] {{ display: none; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
c_h1, c_h2 = st.columns([8, 2])
with c_h1: st.markdown('<div class="main-title">Nexus Omni <span style="font-size:14px; color:gray;">v2.4 Pro</span></div>', unsafe_allow_html=True)
with c_h2: st.session_state.theme_mode = st.selectbox("Appearance", ["Dark", "Light"], label_visibility="collapsed")

# --- 4. THE 5-TAB ARCHITECTURE (FIXED DEFINITION) ---
tab_code, tab_chat, tab_voice, tab_media, tab_test = st.tabs([
    "✍️ Architect", "💬 Intelligent Chat", "🎙️ Urdu/En Voice", "🎨 Media Studio", "🧪 Sandbox"
])

# --- TAB 1: ARCHITECT (GITHUB VAULT) ---
with tab_code:
    col_a, col_v = st.columns([1, 1])
    with col_a:
        st.subheader("🚀 Deploy Production")
        fn = st.text_input("Filename", "new_logic.py")
        cb = st.text_area("Source Code", height=300)
        if st.button("Push to Production", use_container_width=True):
            try:
                try: 
                    f = repo.get_contents(fn); repo.update_file(fn, "Sync", cb, f.sha)
                except: repo.create_file(fn, "Init", cb)
                st.toast("Success!"); st.rerun()
            except Exception as e: st.error(e)
    with col_v:
        st.subheader("📁 Repository Vault")
        try:
            for f in repo.get_contents(""):
                if f.type == "file":
                    with st.expander(f"📄 {f.name}"):
                        st.code(f.decoded_content.decode()[:200] + "...")
                        if st.button("Delete", key=f"del_{f.name}"):
                            repo.delete_file(f.path, "Remove", f.sha); st.rerun()
        except: pass

# --- TAB 2: INTELLIGENT CHAT ---
with tab_chat:
    if "messages" not in st.session_state: st.session_state.messages = []
    cbx = st.container(height=450, border=True)
    for m in st.session_state.messages:
        with cbx.chat_message(m["role"]): st.markdown(m["content"])
    
    q = st.chat_input("Command the Nexus...")
    if q and client:
        st.session_state.messages.append({"role": "user", "content": q})
        with cbx.chat_message("user"): st.markdown(q)
        with cbx.chat_message("assistant"):
            ans = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": q}]).choices[0].message.content
            st.markdown(ans); st.session_state.messages.append({"role": "assistant", "content": ans}); st.rerun()

# --- TAB 3: URDU/ENGLISH VOICE BOT ---
with tab_voice:
    st.subheader("🎙️ Nexus Voice Intelligence")
    st.info("Speak in English or Urdu. I will reply in the same language.")
    audio = mic_recorder(start_prompt="🎤 Click to Speak", stop_prompt="🛑 Stop & Process", key='nexus_mic')
    
    if audio and client:
        with st.spinner("Processing Voice..."):
            # Transcription (Whisper)
            audio_bio = io.BytesIO(audio['bytes'])
            audio_bio.name = "audio.wav"
            transcription = client.audio.transcriptions.create(model="whisper-large-v3", file=audio_bio).text
            st.write(f"**Recognized:** {transcription}")
            
            # Smart Response (Detect En/Ur)
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Reply in the language the user speaks (English or Urdu). Be concise."}, 
                          {"role": "user", "content": transcription}]
            ).choices[0].message.content
            st.write(f"**Nexus:** {res}")
            
            # TTS Output
            tts = gTTS(text=res, lang='ur' if any('\u0600' <= c <= '\u06FF' for c in res) else 'en')
            b_io = io.BytesIO(); tts.write_to_fp(b_io)
            st.audio(b_io.getvalue(), format="audio/mp3", autoplay=True)

# --- TAB 4: MEDIA STUDIO (FREE PICTURE + VEO BRIDGE) ---
with tab_media:
    st.subheader("🎨 Nexus Creative Engine")
    m_t = st.radio("Asset Type", ["Picture (Direct)", "Video (Veo Bridge)"], horizontal=True)
    m_p = st.text_input("Enter Prompt", placeholder="Describe your masterpiece...")
    
    if st.button("✨ Generate", use_container_width=True):
        if m_t == "Picture (Direct)":
            url = f"https://image.pollinations.ai/prompt/{m_p.replace(' ', '%20')}"
            st.image(url, caption="Generated by Nexus Nano-Engine", use_container_width=True)
        else:
            st.success("Veo Prompt Optimized! Copy the code below and paste it to Gemini.")
            st.code(f"Gemini, please use your Veo model to generate a high-fidelity video with audio: {m_p}")

# --- TAB 5: LIVE SANDBOX ---
with tab_test:
    st.subheader("🧪 Production Test Lab")
    tc = st.text_area("Enter Python code to test live:", height=200, value='st.balloons()\nst.success("System Operational!")')
    if st.button("⚙️ Execute"):
        try: exec(tc)
        except Exception as e: st.error(f"Test Error: {e}")
